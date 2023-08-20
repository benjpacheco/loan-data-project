FROM python:3.9.17-slim

RUN pip install -U pip

# Install Python packages
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

# Configure workdir
WORKDIR /home/evidently-fastapi
# Configure PYTHONPATH environment variable
ENV PYTHONPATH=/home/evidently-fastapi

# Launch streamlit application on start up
CMD cd streamlit_app && streamlit run app.py
