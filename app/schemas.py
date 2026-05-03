from pydantic import BaseModel
from typing import Optional

class CreditApplication(BaseModel):
    ORGANIZATION_TYPE: Optional[str] = "undefined"
    EXT_SOURCE_1: Optional[float] = None
    EXT_SOURCE_2: Optional[float] = None
    EXT_SOURCE_3: Optional[float] = None
    INST_DPD_LATE_MEAN: Optional[float] = 0.0
    AMT_CREDIT: Optional[float] = None
    INST_AMT_PAYMENT_SUM: Optional[float] = 0.0
    AMT_ANNUITY: Optional[float] = None
    DAYS_EMPLOYED: Optional[float] = None
    POS_CNT_INSTALMENT_FUTURE_MEAN: Optional[float] = 0.0
    AMT_GOODS_PRICE: Optional[float] = None
    INST_DBD_MEAN: Optional[float] = 0.0
    BURO_DAYS_CREDIT_MAX: Optional[float] = 0.0
    PREV_CNT_PAYMENT_MEAN: Optional[float] = 0.0
    BURO_DAYS_CREDIT_ENDDATE_MAX: Optional[float] = 0.0
    OCCUPATION_TYPE: Optional[str] = "undefined"
    DAYS_ID_PUBLISH: Optional[float] = None
    CC_CNT_DRAWINGS_ATM_CURRENT_MEAN: Optional[float] = 0.0
    OWN_CAR_AGE: Optional[float] = None
    CODE_GENDER: Optional[str] = "XNA"

class PredictionResponse(BaseModel):
    probability: float
    decision: int
    decision_text: str
    threshold: float
    feature_importance: Optional[dict] = None
