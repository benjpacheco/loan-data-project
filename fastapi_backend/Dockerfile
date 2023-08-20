FROM python:3.9.17-slim

RUN pip install -U pip

WORKDIR /app

# Install Python packages
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

RUN pipenv install --system --deploy

COPY [ "app.py", "models.py", "./"]

# Configure PYTHONPATH environment variable
ENV PYTHONPATH=/home/evidently-fastapi


EXPOSE 9696

CMD uvicorn app:app --app-dir fastapi --reload  --host 0.0.0.0 --port 9696
