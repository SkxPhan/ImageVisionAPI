FROM python:3.12-slim

WORKDIR /code

COPY ./pyproject.toml ./poetry.lock* /code/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY ./src /code

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
