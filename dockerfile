FROM python:3.9-slim
RUN mkdir -p /app
COPY app app/
COPY Pipfile /app/
COPY Pipfile.lock /app/
RUN pip install pipenv
WORKDIR /app
RUN pipenv install --system
WORKDIR /
CMD ["uvicorn", "app.app:app", "--host=0.0.0.0", "--port=8000", "--log-config=app/log_config.yml"]