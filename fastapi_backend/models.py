from pydantic import BaseModel

class LoanData(BaseModel):
    emp_title: str
    emp_length: float
    state: str
    homeownership: str
    annual_income: float
    verified_income: str
    debt_to_income: float
    delinq_2y: int
    months_since_last_delinq: float
    earliest_credit_line: int
    inquiries_last_12m: int
    total_credit_lines: int
    open_credit_lines: int
    total_credit_limit: int
    total_credit_utilized: int
    num_collections_last_12m: int
    num_historical_failed_to_pay: int
    months_since_90d_late: float
    current_accounts_delinq: int
    total_collection_amount_ever: int
    current_installment_accounts: int
    accounts_opened_24m: int
    months_since_last_credit_inquiry: float
    num_satisfactory_accounts: int
    num_accounts_120d_past_due: float
    num_accounts_30d_past_due: int
    num_active_debit_accounts: int
    total_debit_limit: int
    num_total_cc_accounts: int
    num_open_cc_accounts: int
    num_cc_carrying_balance: int
    num_mort_accounts: int
    account_never_delinq_percent: float
    tax_liens: int
    public_record_bankrupt: int
    loan_purpose: str
    application_type: str
    loan_amount: int
    term: int
    interest_rate: float
    installment: float
    grade: str
    sub_grade: str
    issue_month: str
    loan_status: str
    initial_listing_status: str
    disbursement_method: str
    balance: float
    paid_total: float
    paid_principal: float
    paid_interest: float
    paid_late_fees: float
