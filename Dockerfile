FROM python:3.12-slim

WORKDIR /backend/app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY app ./backend/app

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]