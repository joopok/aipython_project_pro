"""키움증권 API 요청/응답 Pydantic 모델"""
from typing import Optional, List
from pydantic import BaseModel


# ── 공통 ────────────────────────────────────────

class ContinuationParams(BaseModel):
    """연속조회 공통 파라미터"""
    cont_yn: str = "N"
    next_key: str = ""


# ── 주식정보 요청 ───────────────────────────────

class StockInfoRequest(BaseModel):
    """주식기본정보요청 (ka10001)"""
    stk_cd: str  # 종목코드


class StockBidRequest(BaseModel):
    """주식호가요청 (ka10004)"""
    stk_cd: str


class StockRankRequest(BaseModel):
    """실시간종목조회순위 (ka00198)"""
    qry_tp: str = "1"  # 1:1분, 2:10분, 3:1시간, 4:당일누적, 5:30초


class DailyBalanceRequest(BaseModel):
    """일별잔고수익률 (ka01690)"""
    qry_dt: str  # 조회일자 YYYYMMDD


# ── 주문 요청 ───────────────────────────────────

class BuyOrderRequest(BaseModel):
    """매수주문 (kt10000)"""
    stk_cd: str       # 종목코드
    ord_qty: str      # 주문수량
    ord_uv: str       # 주문단가
    trde_tp: str = "0"  # 매매구분 (0:보통, 3:시장가 등)
    dmst_stex_tp: str = "KRX"  # 거래소구분
    cond_uv: str = ""  # 조건단가


class SellOrderRequest(BaseModel):
    """매도주문 (kt10001)"""
    stk_cd: str
    ord_qty: str
    ord_uv: str = ""
    trde_tp: str = "3"  # 기본: 시장가
    dmst_stex_tp: str = "KRX"
    cond_uv: str = ""


# ── 계좌 요청 ───────────────────────────────────

class DepositDetailRequest(BaseModel):
    """예수금상세현황요청 (kt00001)"""
    qry_tp: str = "3"  # 3:추정조회, 2:일반조회


class AccountEvalRequest(BaseModel):
    """계좌평가현황요청 (kt00004)"""
    qry_tp: str = "0"  # 0:전체, 1:상장폐지종목제외
    dmst_stex_tp: str = "KRX"


# ── 조건검색 요청 (WebSocket) ────────────────────

class ConditionSearchRequest(BaseModel):
    """조건검색 요청 일반 (ka10172)"""
    seq: str              # 조건검색식 일련번호
    stex_tp: str = "K"    # K:KRX전체, Q:코스닥
    cont_yn: str = "N"    # 연속조회여부
    next_key: str = ""    # 연속조회키


class ConditionSearchAllRequest(BaseModel):
    """조건검색 전체 조회 (연속조회 포함)"""
    seq: str
    stex_tp: str = "K"


# ── 조건검색 응답 ───────────────────────────────

class ConditionStockItem(BaseModel):
    """조건검색 결과 종목"""
    stk_cd: str       # 종목코드
    stk_nm: str       # 종목명
    cur_prc: int      # 현재가
    chg_sign: str     # 전일대비부호
    chg_amt: int      # 전일대비금액
    chg_rt: float     # 등락률(%)
    volume: int       # 거래량


class ConditionItem(BaseModel):
    """조건검색식 항목"""
    seq: str
    name: str


class ConditionListResponse(BaseModel):
    """조건검색 목록 응답"""
    status: str = "success"
    api_id: str = "ka10171"
    conditions: List[ConditionItem]
    total_count: int


class ConditionSearchResponse(BaseModel):
    """조건검색 일반 응답 (ka10172)"""
    status: str = "success"
    api_id: str = "ka10172"
    stocks: List[ConditionStockItem]
    total_count: int
    cont_yn: str = "N"
    next_key: str = ""
    condition_list: Optional[List[ConditionItem]] = None


# ── 공통 응답 ───────────────────────────────────

class KiwoomApiResponse(BaseModel):
    """키움 API 공통 응답 래퍼"""
    status: str = "success"
    api_id: str
    data: dict
    cont_yn: str = "N"
    next_key: str = ""
