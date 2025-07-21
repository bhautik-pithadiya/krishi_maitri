from fastapi import APIRouter
from app.models.finance import FinanceRequest, FinanceResponse

router = APIRouter()

@router.post("/loan", response_model=FinanceResponse)
def get_loan_info(request: FinanceRequest):
    # Dummy logic for demonstration
    return FinanceResponse(
        scheme="Kisan Credit Card",
        eligibility="Eligible",
        interest_rate=4.0,
        max_loan_amount=150000
    )