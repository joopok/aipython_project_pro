"""
키움증권 WebSocket 클라이언트
- 조건검색 목록 (ka10171 / CNSRLST)
- 조건검색 일반 (ka10172 / CNSRREQ search_type=0)
- WebSocket 연결 → LOGIN → CNSRLST → CNSRREQ 전체 흐름을 HTTP 브리지로 제공

공식 키움 WebSocket 흐름:
  1. wss://api.kiwoom.com:10000/api/dostk/websocket 연결
  2. LOGIN (REST 토큰 사용)
  3. CNSRLST (조건검색 목록 — CNSRREQ 전 필수)
  4. CNSRREQ (search_type=0: 일반 조건검색)
  5. PING 수신 시 즉시 에코 응답
"""
import asyncio
import json
import logging
import ssl
import time
from typing import Optional

try:
    import websockets
except ImportError:
    websockets = None

from app.services.kiwoom_client import kiwoom_client
from app.core.kiwoom_config import KIWOOM_WS_URL, KIWOOM_IS_MOCK

logger = logging.getLogger(__name__)

# WebSocket 경로
_WS_PATH = "/api/dostk/websocket"

# 타임아웃 (초)
_LOGIN_TIMEOUT = 10
_RECV_TIMEOUT = 10       # 개별 recv 타임아웃
_TOTAL_TIMEOUT = 30      # _recv_until 전체 타임아웃


def _get_ws_url() -> str:
    """프로필 기반 WebSocket URL (config의 KIWOOM_WS_URL + 경로)"""
    return f"{KIWOOM_WS_URL}{_WS_PATH}"


def _safe_parse(raw) -> dict:
    """WebSocket 메시지를 안전하게 파싱"""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    if not isinstance(raw, str):
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"JSON 파싱 실패: {raw[:200]}")
        return {}


def _parse_condition_list(resp: dict) -> list:
    """CNSRLST 응답 파싱 → [{"seq": str, "name": str}, ...]

    키움 실제 응답 형식: {"data": [["0","조건명1"], ["1","조건명2"], ...]}
    """
    conditions = []
    data_list = resp.get("data", [])
    if isinstance(data_list, list):
        for item in data_list:
            # 배열 형식: ["seq", "name"]
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                seq = str(item[0]).strip()
                name = str(item[1]).strip()
                if seq or name:
                    conditions.append({"seq": seq, "name": name})
            # dict 형식 (하위 호환)
            elif isinstance(item, dict):
                seq = item.get("seq", "") or item.get("cns_idx", "")
                name = item.get("name", "") or item.get("cns_nm", "") or item.get("condition_name", "")
                if seq or name:
                    conditions.append({"seq": str(seq).strip(), "name": str(name).strip()})
    logger.info(f"CNSRLST 파싱 완료: {len(conditions)}개 조건식")
    return conditions


def _parse_stock_item(item: dict) -> Optional[dict]:
    """조건검색 결과 종목 항목 파싱

    키움 숫자 키 매핑:
      9001 = 종목코드, 302 = 종목명, 10 = 현재가
      25 = 전일대비부호, 11 = 전일대비, 12 = 등락률(×1000), 13 = 거래량
    """
    if not isinstance(item, dict):
        return None

    code = item.get("9001", "") or item.get("stk_cd", "") or item.get("code", "")
    code = str(code).strip().lstrip("A")

    if not code:
        return None

    name = item.get("302", "") or item.get("stk_nm", "") or item.get("name", "")

    # 현재가 (부호 처리)
    price_raw = item.get("10", "") or item.get("cur_prc", "0")
    try:
        price = abs(int(str(price_raw).strip()))
    except (ValueError, TypeError):
        price = 0

    # 등락률 (×1000 정수)
    rate_raw = item.get("12", "") or item.get("chg_rt", "0")
    try:
        rate = int(str(rate_raw).strip()) / 1000
    except (ValueError, TypeError):
        rate = 0.0

    # 전일대비 부호
    sign_raw = item.get("25", "3")
    sign_map = {"1": "상한", "2": "상승", "3": "보합", "4": "하한", "5": "하락"}
    sign = sign_map.get(str(sign_raw).strip(), "보합")

    # 전일대비
    diff_raw = item.get("11", "0")
    try:
        diff = abs(int(str(diff_raw).strip()))
    except (ValueError, TypeError):
        diff = 0

    # 거래량
    vol_raw = item.get("13", "0")
    try:
        volume = int(str(vol_raw).strip())
    except (ValueError, TypeError):
        volume = 0

    return {
        "stk_cd": code,
        "stk_nm": str(name).strip(),
        "cur_prc": price,
        "chg_sign": sign,
        "chg_amt": diff,
        "chg_rt": round(rate, 2),
        "volume": volume,
    }


def _parse_condition_search_result(resp: dict) -> dict:
    """CNSRREQ 응답 파싱"""
    stocks = []
    data = resp.get("data", [])

    if isinstance(data, list):
        for item in data:
            stock = _parse_stock_item(item)
            if stock:
                stocks.append(stock)

    return {
        "stocks": stocks,
        "total_count": len(stocks),
        "cont_yn": resp.get("cont_yn", "N"),
        "next_key": resp.get("next_key", ""),
    }


def _validate_seq(seq: str) -> str:
    """조건검색식 번호 검증 — 빈 값만 거부"""
    seq_str = str(seq).strip()
    if not seq_str:
        raise ValueError("조건검색식 번호(seq)가 비어 있습니다")
    return seq_str


async def _recv_until(ws, trnm: str, total_timeout: float = _TOTAL_TIMEOUT) -> dict:
    """특정 trnm 응답이 올 때까지 수신 (PING은 에코)

    전체 타임아웃(deadline)으로 PING 루프에서 영원히 대기하는 것을 방지.
    """
    deadline = time.monotonic() + total_timeout
    msg_count = 0

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"[{trnm}] 응답 대기 타임아웃 ({total_timeout}초 초과, 수신 메시지 {msg_count}개)")

        per_recv_timeout = min(_RECV_TIMEOUT, remaining)

        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=per_recv_timeout)
        except asyncio.TimeoutError:
            # 개별 recv 타임아웃 → 전체 deadline 확인 후 재시도 또는 종료
            if time.monotonic() >= deadline:
                raise TimeoutError(f"[{trnm}] 응답 대기 타임아웃 ({total_timeout}초 초과, 수신 메시지 {msg_count}개)")
            continue

        msg_count += 1
        resp = _safe_parse(raw)
        recv_trnm = resp.get("trnm", "")

        # PING 에코 (키움 공식 요구사항)
        if recv_trnm == "PING":
            await ws.send(json.dumps(resp))
            logger.info(f"PING 에코 전송 (대기중={trnm})")
            continue

        # 수신된 모든 메시지 로깅
        raw_preview = str(raw)[:500] if raw else "(empty)"
        logger.info(f"[WS 수신] trnm={recv_trnm}, 대기중={trnm}, keys={list(resp.keys())}, raw={raw_preview}")

        if recv_trnm == trnm:
            logger.info(f"[{trnm}] 응답 매칭: return_code={resp.get('return_code')}")
            return resp

        # trnm이 없는 경우 — 키움이 trnm 없이 데이터만 보내는 경우
        if not recv_trnm and resp:
            logger.warning(f"[WS] trnm 없는 응답 수신, {trnm}에 할당: {raw_preview[:300]}")
            return resp

        # 예상치 못한 trnm — 로깅 후 무시
        logger.warning(f"[WS] 무시된 메시지: trnm={recv_trnm} (대기중={trnm})")


async def _ws_connect_and_login():
    """WebSocket 연결 + LOGIN → ws 객체 반환"""
    if websockets is None:
        raise RuntimeError("websockets 패키지가 필요합니다: pip install websockets")

    token = await kiwoom_client.get_token()
    ws_url = _get_ws_url()

    # 키움 Mock/Real 서버 모두 자체 서명 인증서 사용 → SSL 검증 비활성화
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    logger.info(f"WebSocket 연결: {ws_url} (mock={KIWOOM_IS_MOCK})")
    ws = await websockets.connect(ws_url, ssl=ssl_ctx, max_size=10 * 1024 * 1024)

    try:
        # LOGIN
        login_msg = {"trnm": "LOGIN", "token": token}
        logger.info(f"LOGIN 전송")
        await ws.send(json.dumps(login_msg))

        raw = await asyncio.wait_for(ws.recv(), timeout=_LOGIN_TIMEOUT)
        logger.info(f"LOGIN 응답 수신: {str(raw)[:300]}")
        resp = _safe_parse(raw)

        # return_code 확인 (0 = 성공)
        rc = resp.get("return_code")
        if resp.get("trnm") == "LOGIN" and rc != 0:
            msg = resp.get("return_msg", "알 수 없는 오류")
            raise RuntimeError(f"WebSocket 로그인 실패 (code={rc}): {msg}")

        logger.info("WebSocket LOGIN 성공")
        return ws
    except Exception:
        await ws.close()
        raise


async def _ws_session(operations: list) -> list:
    """WebSocket 세션: LOGIN 후 operations를 순서대로 실행."""
    ws = await _ws_connect_and_login()
    try:
        results = []
        for op in operations:
            result = await op(ws)
            results.append(result)
        return results
    except TimeoutError as e:
        logger.error(f"WebSocket 세션 타임아웃: {e}")
        raise
    finally:
        await ws.close()
        logger.info("WebSocket 연결 종료")


# ── 공개 API ────────────────────────────────────


async def get_condition_list() -> list:
    """조건검색 목록 조회 (ka10171 / CNSRLST)

    Returns:
        [{"seq": "1", "name": "급등주 필터"}, ...]
    """
    async def _op(ws):
        logger.info("CNSRLST 전송")
        await ws.send(json.dumps({"trnm": "CNSRLST"}))
        resp = await _recv_until(ws, "CNSRLST")
        return _parse_condition_list(resp)

    results = await _ws_session([_op])
    return results[0]


async def condition_search_normal(
    seq: str,
    stex_tp: str = "K",
    cont_yn: str = "N",
    next_key: str = "",
) -> dict:
    """조건검색 요청 일반 (ka10172 / CNSRREQ search_type=0)

    흐름: LOGIN → CNSRLST(필수) → CNSRREQ(search_type=0)
    """
    seq_str = _validate_seq(seq)
    if stex_tp not in ("K", "Q"):
        raise ValueError(f"유효하지 않은 거래소 구분: {stex_tp} (K 또는 Q)")

    async def _cnsrlst(ws):
        logger.info("CNSRLST 전송 (선행 필수)")
        await ws.send(json.dumps({"trnm": "CNSRLST"}))
        resp = await _recv_until(ws, "CNSRLST")
        return _parse_condition_list(resp)

    async def _cnsrreq(ws):
        # CNSRLST → CNSRREQ 사이 안정화 대기
        await asyncio.sleep(0.5)

        param = {
            "trnm": "CNSRREQ",
            "seq": seq_str,
            "search_type": "0",
            "stex_tp": stex_tp,
            "cont_yn": cont_yn,
            "next_key": next_key,
        }
        param_json = json.dumps(param)
        logger.info(f"CNSRREQ 전송: {param_json}")
        await ws.send(param_json)
        resp = await _recv_until(ws, "CNSRREQ")

        rc = resp.get("return_code")
        if rc is not None and rc != 0:
            msg = resp.get("return_msg", "알 수 없는 오류")
            raise RuntimeError(f"조건검색 실패 (code={rc}): {msg}")

        return _parse_condition_search_result(resp)

    results = await _ws_session([_cnsrlst, _cnsrreq])
    condition_list = results[0]
    search_result = results[1]
    search_result["condition_list"] = condition_list
    return search_result


async def condition_search_all(
    seq: str,
    stex_tp: str = "K",
) -> dict:
    """조건검색 연속조회로 전체 종목 조회 (단일 세션)"""
    seq_str = _validate_seq(seq)
    if stex_tp not in ("K", "Q"):
        raise ValueError(f"유효하지 않은 거래소 구분: {stex_tp} (K 또는 Q)")

    all_stocks = []
    max_pages = 20

    async def _full_search(ws):
        nonlocal all_stocks

        # 1) CNSRLST (필수 선행)
        logger.info("CNSRLST 전송 (선행 필수)")
        await ws.send(json.dumps({"trnm": "CNSRLST"}))
        await _recv_until(ws, "CNSRLST")

        # CNSRLST → CNSRREQ 사이 안정화 대기
        await asyncio.sleep(0.5)

        # 2) CNSRREQ 반복
        c_yn = "N"
        n_key = ""
        page = 0

        while page < max_pages:
            param = {
                "trnm": "CNSRREQ",
                "seq": seq_str,
                "search_type": "0",
                "stex_tp": stex_tp,
                "cont_yn": c_yn,
                "next_key": n_key,
            }
            logger.info(f"CNSRREQ 전송 (page={page}): cont_yn={c_yn}")
            await ws.send(json.dumps(param))
            resp = await _recv_until(ws, "CNSRREQ")

            rc = resp.get("return_code")
            if rc is not None and rc != 0:
                msg = resp.get("return_msg", "알 수 없는 오류")
                raise RuntimeError(f"조건검색 실패 (code={rc}): {msg}")

            result = _parse_condition_search_result(resp)
            all_stocks.extend(result.get("stocks", []))

            if result.get("cont_yn") != "Y" or not result.get("next_key"):
                break

            c_yn = "Y"
            n_key = result["next_key"]
            page += 1

    ws = await _ws_connect_and_login()
    try:
        await _full_search(ws)
    except TimeoutError as e:
        logger.error(f"전체 조건검색 타임아웃: {e}")
        raise
    finally:
        await ws.close()
        logger.info("WebSocket 연결 종료")

    return {
        "stocks": all_stocks,
        "total_count": len(all_stocks),
    }
