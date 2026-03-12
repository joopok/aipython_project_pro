"""
키움증권 REST API 라우터
- chapter 패턴을 HTTP 엔드포인트로 변환
- 모든 키움 API는 POST 방식
"""
import logging
from fastapi import APIRouter, HTTPException, Query

from app.services.kiwoom_client import kiwoom_client
from app.services import kiwoom_ws_client
from app.schemas.kiwoom import (
    StockInfoRequest,
    StockBidRequest,
    StockRankRequest,
    DailyBalanceRequest,
    BuyOrderRequest,
    SellOrderRequest,
    DepositDetailRequest,
    AccountEvalRequest,
    KiwoomApiResponse,
    ConditionSearchRequest,
    ConditionSearchAllRequest,
    ConditionListResponse,
    ConditionSearchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_response(api_id: str, data: dict) -> dict:
    """키움 API 응답을 표준 형식으로 래핑"""
    meta = data.pop("_meta", {})
    return {
        "status": "success",
        "api_id": api_id,
        "data": data,
        "cont_yn": meta.get("cont_yn", "N"),
        "next_key": meta.get("next_key", ""),
    }


# ── 토큰 ────────────────────────────────────────

@router.post("/token", summary="접근토큰 발급 (au10001)")
async def get_token():
    """키움 API 접근토큰을 발급합니다."""
    try:
        token = await kiwoom_client.get_token()
        return {"status": "success", "token": token}
    except Exception as e:
        logger.error(f"토큰 발급 실패: {e}")
        raise HTTPException(status_code=500, detail=f"토큰 발급 실패: {str(e)}")


# ── 주식정보 (ka) ────────────────────────────────

@router.post("/stock/info", response_model=KiwoomApiResponse, summary="주식기본정보 (ka10001)")
async def stock_info(
    req: StockInfoRequest,
    cont_yn: str = Query("N", description="연속조회여부"),
    next_key: str = Query("", description="연속조회키"),
):
    """종목코드로 주식 기본정보를 조회합니다."""
    try:
        data = await kiwoom_client.stock_info(req.stk_cd, cont_yn=cont_yn, next_key=next_key)
        return _build_response("ka10001", data)
    except Exception as e:
        logger.error(f"주식기본정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock/bid", response_model=KiwoomApiResponse, summary="주식호가 (ka10004)")
async def stock_bid(
    req: StockBidRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """종목코드로 주식 호가를 조회합니다."""
    try:
        data = await kiwoom_client.stock_bid(req.stk_cd, cont_yn=cont_yn, next_key=next_key)
        return _build_response("ka10004", data)
    except Exception as e:
        logger.error(f"호가 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock/rank", response_model=KiwoomApiResponse, summary="실시간종목순위 (ka00198)")
async def stock_rank(
    req: StockRankRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """실시간 종목 조회 순위를 가져옵니다."""
    try:
        data = await kiwoom_client.stock_rank(req.qry_tp, cont_yn=cont_yn, next_key=next_key)
        return _build_response("ka00198", data)
    except Exception as e:
        logger.error(f"종목순위 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/account/daily-balance", response_model=KiwoomApiResponse, summary="일별잔고수익률 (ka01690)")
async def daily_balance(
    req: DailyBalanceRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """일별 잔고 수익률을 조회합니다."""
    try:
        data = await kiwoom_client.daily_balance(req.qry_dt, cont_yn=cont_yn, next_key=next_key)
        return _build_response("ka01690", data)
    except Exception as e:
        logger.error(f"일별잔고 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 주문 (kt) ───────────────────────────────────

@router.post("/order/buy", response_model=KiwoomApiResponse, summary="매수주문 (kt10000)")
async def buy_order(
    req: BuyOrderRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """주식 매수 주문을 실행합니다."""
    try:
        data = await kiwoom_client.buy_order(
            stk_cd=req.stk_cd,
            ord_qty=req.ord_qty,
            ord_uv=req.ord_uv,
            trde_tp=req.trde_tp,
            dmst_stex_tp=req.dmst_stex_tp,
            cond_uv=req.cond_uv,
            cont_yn=cont_yn,
            next_key=next_key,
        )
        return _build_response("kt10000", data)
    except Exception as e:
        logger.error(f"매수주문 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order/sell", response_model=KiwoomApiResponse, summary="매도주문 (kt10001)")
async def sell_order(
    req: SellOrderRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """주식 매도 주문을 실행합니다."""
    try:
        data = await kiwoom_client.sell_order(
            stk_cd=req.stk_cd,
            ord_qty=req.ord_qty,
            ord_uv=req.ord_uv,
            trde_tp=req.trde_tp,
            dmst_stex_tp=req.dmst_stex_tp,
            cond_uv=req.cond_uv,
            cont_yn=cont_yn,
            next_key=next_key,
        )
        return _build_response("kt10001", data)
    except Exception as e:
        logger.error(f"매도주문 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 계좌 (kt) ───────────────────────────────────

@router.post("/account/deposit", response_model=KiwoomApiResponse, summary="예수금상세 (kt00001)")
async def deposit_detail(
    req: DepositDetailRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """예수금 상세 현황을 조회합니다."""
    try:
        data = await kiwoom_client.deposit_detail(req.qry_tp, cont_yn=cont_yn, next_key=next_key)
        return _build_response("kt00001", data)
    except Exception as e:
        logger.error(f"예수금 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/account/evaluation", response_model=KiwoomApiResponse, summary="계좌평가 (kt00004)")
async def account_evaluation(
    req: AccountEvalRequest,
    cont_yn: str = Query("N"),
    next_key: str = Query(""),
):
    """계좌 평가 현황을 조회합니다."""
    try:
        data = await kiwoom_client.account_evaluation(
            req.qry_tp, req.dmst_stex_tp, cont_yn=cont_yn, next_key=next_key
        )
        return _build_response("kt00004", data)
    except Exception as e:
        logger.error(f"계좌평가 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 조건검색 (WebSocket → HTTP 브리지) ──────────

@router.get("/condition/list", response_model=ConditionListResponse, summary="조건검색 목록 (ka10171) GET")
@router.post("/condition/list", response_model=ConditionListResponse, summary="조건검색 목록 (ka10171) POST")
async def condition_list():
    """HTS에 저장된 조건검색식 목록을 조회합니다.

    WebSocket(CNSRLST)을 통해 조건검색식 목록을 가져옵니다.
    """
    try:
        conditions = await kiwoom_ws_client.get_condition_list()
        return {
            "status": "success",
            "api_id": "ka10171",
            "conditions": conditions,
            "total_count": len(conditions),
        }
    except Exception as e:
        logger.error(f"조건검색 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/condition/search", response_model=ConditionSearchResponse, summary="조건검색 일반 (ka10172) GET")
async def condition_search_normal_get(
    seq: str = Query(..., description="조건검색식 일련번호"),
    stex_tp: str = Query("K", description="거래소 구분 (K=KRX전체, Q=코스닥)"),
    cont_yn: str = Query("N", description="연속조회여부"),
    next_key: str = Query("", description="연속조회키"),
):
    """조건검색 요청 일반 (GET) — 브라우저에서 바로 호출 가능

    예시: `/api/kiwoom/condition/search?seq=4&stex_tp=K`
    """
    return await _do_condition_search(seq, stex_tp, cont_yn, next_key)


@router.post("/condition/search", response_model=ConditionSearchResponse, summary="조건검색 일반 (ka10172) POST")
async def condition_search_normal_post(req: ConditionSearchRequest):
    """조건검색 요청 일반 (POST) — JSON Body로 호출

    ```json
    {"seq": "4", "stex_tp": "K"}
    ```
    """
    return await _do_condition_search(req.seq, req.stex_tp, req.cont_yn, req.next_key)


async def _do_condition_search(seq: str, stex_tp: str, cont_yn: str, next_key: str) -> dict:
    """조건검색 일반 공통 처리"""
    try:
        result = await kiwoom_ws_client.condition_search_normal(
            seq=seq, stex_tp=stex_tp, cont_yn=cont_yn, next_key=next_key,
        )
        return {"status": "success", "api_id": "ka10172", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"조건검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/condition/search-all", response_model=ConditionSearchResponse, summary="조건검색 전체 (ka10172) GET")
async def condition_search_all_get(
    seq: str = Query(..., description="조건검색식 일련번호"),
    stex_tp: str = Query("K", description="거래소 구분"),
):
    """조건검색 전체 조회 (GET) — 연속조회 포함"""
    return await _do_condition_search_all(seq, stex_tp)


@router.post("/condition/search-all", response_model=ConditionSearchResponse, summary="조건검색 전체 (ka10172) POST")
async def condition_search_all_post(req: ConditionSearchAllRequest):
    """조건검색 전체 조회 (POST) — 연속조회 포함"""
    return await _do_condition_search_all(req.seq, req.stex_tp)


async def _do_condition_search_all(seq: str, stex_tp: str) -> dict:
    """조건검색 전체 공통 처리"""
    try:
        result = await kiwoom_ws_client.condition_search_all(seq=seq, stex_tp=stex_tp)
        return {"status": "success", "api_id": "ka10172", **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"조건검색 전체 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── 서버 상태 ────────────────────────────────────

@router.get("/status", summary="키움 API 연결 상태")
async def kiwoom_status():
    """키움 API 연결 상태 및 설정을 확인합니다."""
    from app.core.kiwoom_config import (
        KIWOOM_HOST_URL,
        KIWOOM_ACTIVE_PROFILE,
        KIWOOM_IS_MOCK,
        KIWOOM_ACCOUNT,
    )
    return {
        "status": "ok",
        "profile": KIWOOM_ACTIVE_PROFILE,
        "is_mock": KIWOOM_IS_MOCK,
        "host_url": KIWOOM_HOST_URL,
        "account": KIWOOM_ACCOUNT[:4] + "****" if KIWOOM_ACCOUNT else "",
        "token_cached": kiwoom_client._token is not None,
    }
