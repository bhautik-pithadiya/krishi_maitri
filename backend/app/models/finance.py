from pydantic import BaseModel

class FinanceRequest(BaseModel):
    farmer_id: str
    crop: str

class FinanceResponse(BaseModel):
    scheme: str
    eligibility: str
    interest_rate: float
    max_loan_amount: int