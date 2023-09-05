import httpx


def test_predict_endpoint():
    data = {
        "emp_title": "Software Engineer",
        "emp_length": 5.0,
        "state": "CA",
        "homeownership": "OWN",
        "annual_income": 85000.0,
        "verified_income": "Verified",
        "debt_to_income": 22.0,
        "delinq_2y": 1,
        "months_since_last_delinq": 15.0,
        "earliest_credit_line": 2005,
        "inquiries_last_12m": 3,
        "total_credit_lines": 20,
        "open_credit_lines": 12,
        "total_credit_limit": 50000,
        "total_credit_utilized": 30000,
        "num_collections_last_12m": 0,
        "num_historical_failed_to_pay": 2,
        "months_since_90d_late": 5.0,
        "current_accounts_delinq": 0,
        "total_collection_amount_ever": 0,
        "current_installment_accounts": 5,
        "accounts_opened_24m": 5,
        "months_since_last_credit_inquiry": 2.0,
        "num_satisfactory_accounts": 18,
        "num_accounts_120d_past_due": 0.0,
        "num_accounts_30d_past_due": 0,
        "num_active_debit_accounts": 8,
        "total_debit_limit": 15000,
        "num_total_cc_accounts": 5,
        "num_open_cc_accounts": 3,
        "num_cc_carrying_balance": 4,
        "num_mort_accounts": 2,
        "account_never_delinq_percent": 90.0,
        "tax_liens": 0,
        "public_record_bankrupt": 0,
        "loan_purpose": "debt_consolidation",
        "application_type": "individual",
        "loan_amount": 15000,
        "term": 36,
        "interest_rate": 6.5,
        "installment": 460.32,
        "grade": "A",
        "sub_grade": "A2",
        "issue_month": "Jan-2023",
        "loan_status": "Current",
        "initial_listing_status": "w",
        "disbursement_method": "Cash",
        "balance": 10000.0,
        "paid_total": 5000.0,
        "paid_principal": 3000.0,
        "paid_interest": 1800.0,
        "paid_late_fees": 200.0,
    }

    url = "http://fastapi_app:9696/predict"
    response = httpx.post(url, json=data)

    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] in ["Charged Off", "Not Charged Off"]
