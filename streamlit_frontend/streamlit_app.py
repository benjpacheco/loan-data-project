from typing import Text
import os
import requests
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components


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
        col1.markdown(f"<a style='display: block; text-align: center;' href={repo_link}>Source code</a>", unsafe_allow_html=True)
        col2.markdown(f"<a style='display: block; text-align: center;' href={evidently_docs}>Evidently docs</a>", unsafe_allow_html=True)
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


if __name__ == '__main__':
    # Configure some styles
    set_page_container_style()
    # Sidebar: Logo and links
    display_sidebar_header()

    host: Text = os.getenv('FASTAPI_APP_HOST', 'localhost')
    base_route: Text = f'http://{host}:9696'

    try:
        window_size: int = st.sidebar.number_input(label='window_size', min_value=1, step=1, value=3000)
        clicked_model_performance: bool = st.sidebar.button(label='Model performance')
        clicked_target_drift: bool = st.sidebar.button(label='Target drift')

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

        if report_selected:
            resp: requests.Response = requests.get(request_url)
            display_header(report_name, window_size)
            display_report(resp.content)

    except Exception as e:
        st.error(e)
