"""
키움증권 REST API 클라이언트
- 토큰 발급/캐싱
- 공통 API 호출 메서드
- chapter 패턴을 서비스 레이어로 통합
"""
import time
import logging
import httpx

from app.core.kiwoom_config import (
    KIWOOM_HOST_URL,
    KIWOOM_APP_KEY,
    KIWOOM_SECRET_KEY,
)

logger = logging.getLogger(__name__)


class KiwoomClient:
    """키움증권 REST API 클라이언트 (싱글톤 패턴)"""

    def __init__(self):
        self._token: str | None = None
        self._token_expires_at: float = 0
        self._http = httpx.AsyncClient(
            base_url=KIWOOM_HOST_URL,
            verify=False,  # 키움 API self-signed 인증서 허용
            timeout=30.0,
        )

    # ── 토큰 관리 ──────────────────────────────────

    async def get_token(self) -> str:
        """접근토큰 발급 (au10001). 유효기간 내 캐싱."""
        if self._token and time.time() < self._token_expires_at:
            return self._token

        data = {
            "grant_type": "client_credentials",
            "appkey": KIWOOM_APP_KEY,
            "secretkey": KIWOOM_SECRET_KEY,
        }
        resp = await self._http.post(
            "/oauth2/token",
            json=data,
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )
        resp.raise_for_status()
        result = resp.json()

        self._token = result.get("token")
        # 키움 토큰 유효기간: 약 24시간, 여유를 두고 23시간으로 캐싱
        self._token_expires_at = time.time() + 23 * 3600

        logger.info("키움 API 토큰 발급 완료")
        return self._token

    # ── 공통 API 호출 ──────────────────────────────

    async def call_api(
        self,
        endpoint: str,
        api_id: str,
        params: dict,
        cont_yn: str = "N",
        next_key: str = "",
    ) -> dict:
        """
        키움 REST API 공통 호출 메서드.
        모든 키움 API는 POST + header에 api-id 패턴.
        """
        token = await self.get_token()

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {token}",
            "cont-yn": cont_yn,
            "next-key": next_key,
            "api-id": api_id,
        }

        resp = await self._http.post(endpoint, json=params, headers=headers)
        resp.raise_for_status()

        # 응답 헤더에서 연속조회 정보 추출
        resp_data = resp.json()
        resp_data["_meta"] = {
            "cont_yn": resp.headers.get("cont-yn", "N"),
            "next_key": resp.headers.get("next-key", ""),
            "api_id": resp.headers.get("api-id", api_id),
        }

        return resp_data

    # ── 주식정보 (ka) ──────────────────────────────

    async def stock_info(self, stk_cd: str, **kwargs) -> dict:
        """주식기본정보요청 (ka10001)"""
        return await self.call_api(
            "/api/dostk/stkinfo", "ka10001", {"stk_cd": stk_cd}, **kwargs
        )

    async def stock_bid(self, stk_cd: str, **kwargs) -> dict:
        """주식호가요청 (ka10004)"""
        return await self.call_api(
            "/api/dostk/mrkcond", "ka10004", {"stk_cd": stk_cd}, **kwargs
        )

    async def stock_rank(self, qry_tp: str = "1", **kwargs) -> dict:
        """실시간종목조회순위 (ka00198)"""
        return await self.call_api(
            "/api/dostk/stkinfo", "ka00198", {"qry_tp": qry_tp}, **kwargs
        )

    async def daily_balance(self, qry_dt: str, **kwargs) -> dict:
        """일별잔고수익률 (ka01690)"""
        return await self.call_api(
            "/api/dostk/acnt", "ka01690", {"qry_dt": qry_dt}, **kwargs
        )

    # ── 주문 (kt) ──────────────────────────────────

    async def buy_order(
        self,
        stk_cd: str,
        ord_qty: str,
        ord_uv: str,
        trde_tp: str = "0",
        dmst_stex_tp: str = "KRX",
        cond_uv: str = "",
        **kwargs,
    ) -> dict:
        """주식 매수주문 (kt10000)"""
        params = {
            "dmst_stex_tp": dmst_stex_tp,
            "stk_cd": stk_cd,
            "ord_qty": str(ord_qty),
            "ord_uv": str(ord_uv),
            "trde_tp": trde_tp,
            "cond_uv": cond_uv,
        }
        return await self.call_api("/api/dostk/ordr", "kt10000", params, **kwargs)

    async def sell_order(
        self,
        stk_cd: str,
        ord_qty: str,
        ord_uv: str = "",
        trde_tp: str = "3",
        dmst_stex_tp: str = "KRX",
        cond_uv: str = "",
        **kwargs,
    ) -> dict:
        """주식 매도주문 (kt10001)"""
        params = {
            "dmst_stex_tp": dmst_stex_tp,
            "stk_cd": stk_cd,
            "ord_qty": str(ord_qty),
            "ord_uv": str(ord_uv),
            "trde_tp": trde_tp,
            "cond_uv": cond_uv,
        }
        return await self.call_api("/api/dostk/ordr", "kt10001", params, **kwargs)

    # ── 계좌 (kt) ──────────────────────────────────

    async def deposit_detail(self, qry_tp: str = "3", **kwargs) -> dict:
        """예수금상세현황요청 (kt00001)"""
        return await self.call_api(
            "/api/dostk/acnt", "kt00001", {"qry_tp": qry_tp}, **kwargs
        )

    async def account_evaluation(
        self, qry_tp: str = "0", dmst_stex_tp: str = "KRX", **kwargs
    ) -> dict:
        """계좌평가현황요청 (kt00004)"""
        params = {"qry_tp": qry_tp, "dmst_stex_tp": dmst_stex_tp}
        return await self.call_api("/api/dostk/acnt", "kt00004", params, **kwargs)

    # ── 정리 ───────────────────────────────────────

    async def close(self):
        """HTTP 클라이언트 정리"""
        await self._http.aclose()


# 싱글톤 인스턴스
kiwoom_client = KiwoomClient()
