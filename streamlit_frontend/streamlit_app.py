import os
from typing import Text

import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
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


def set_page_container_style() -> None:
    """Set report container style."""
    margins_css = """
    <style>
        /* Configuration of paddings of containers inside main area */
        .main > div {
            max-width: 100%;
            padding-left: 10%;
        }

        /*Font size in tabs */
        button[data-baseweb="tab"] div p {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)


def display_sidebar_header() -> None:
    """Display sidebar header with logo and links."""
    logo = Image.open("static/logo.png")
    with st.sidebar:
        st.image(logo, use_column_width=True)
        col1, col2 = st.columns(2)
        repo_link: Text = '#'
        evidently_docs: Text = 'https://docs.evidentlyai.com/'
        col1.markdown(
            f"<a style='display: block; text-align: center;' href={repo_link}>Source code</a>",
            unsafe_allow_html=True,
        )
        col2.markdown(
            f"<a style='display: block; text-align: center;' href={evidently_docs}>Evidently docs</a>",
            unsafe_allow_html=True,
        )
        st.header('')  # add space between logo and selectors


def display_header(report_name: Text, window_size: int) -> None:
    """Display report header."""
    st.header(f'Report: {report_name}')
    st.caption(f'Window size: {window_size}')


@st.cache_data
def display_report(report: Text) -> Text:
    """Display report."""
    components.html(report, width=1000, height=500, scrolling=True)
    return report


def display_prediction_form() -> None:
    """Display prediction form."""
    st.header('Make a Prediction')

    # Create input fields for each attribute of LoanData
    loan_data = LoanData()
    loan_data_dict = loan_data.dict()  # Convert to dictionary for iteration

    for attr, value in loan_data_dict.items():
        if isinstance(value, (str, Text)):
            loan_data_dict[attr] = st.text_input(attr.replace('_', ' ').title(), value)
        elif isinstance(value, float):
            loan_data_dict[attr] = st.number_input(
                attr.replace('_', ' ').title(), value=value
            )
        elif isinstance(value, int):
            loan_data_dict[attr] = st.number_input(
                attr.replace('_', ' ').title(), value=int(value)
            )

    # Create a button to make the prediction
    if st.button('Predict'):
        # Prepare the data to be sent to the FastAPI endpoint
        prediction_data = loan_data(
            **loan_data_dict
        ).dict()  # Convert back to LoanData instance
        prediction_url = f'http://{host}:9696/predict'
        response = requests.post(prediction_url, json=prediction_data)

        # Display the prediction result
        prediction_result = response.json().get('prediction')
        st.success(f'Prediction: {prediction_result}')


if __name__ == '__main__':
    # Configure some styles
    set_page_container_style()
    # Sidebar: Logo and links
    display_sidebar_header()

    host: Text = os.getenv('FASTAPI_APP_HOST', 'fastapi_app')
    base_route: Text = f'http://{host}:9696'

    try:
        window_size: int = st.sidebar.number_input(
            label='window_size', min_value=1, step=1, value=3000
        )
        clicked_model_performance: bool = st.sidebar.button(label='Model performance')
        clicked_target_drift: bool = st.sidebar.button(label='Target drift')
        clicked_make_prediction: bool = st.sidebar.button(label='Make Prediction')

        report_selected: bool = False
        request_url: Text = base_route
        report_name: Text = ''

        if clicked_model_performance:
            report_selected = True
            request_url += f'/monitor-model?window_size={window_size}'
            report_name = 'Model performance'

        if clicked_target_drift:
            report_selected = True
            request_url += f'/monitor-target?window_size={window_size}'
            report_name = 'Target drift'

        if clicked_make_prediction:
            display_prediction_form()

        if report_selected:
            resp: requests.Response = requests.get(request_url)
            display_header(report_name, window_size)
            display_report(resp.content)

    except Exception as e:
        st.error(e)
