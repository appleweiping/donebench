FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends git make ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY donebench ./donebench

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]"

COPY . .

CMD ["make", "smoke"]
