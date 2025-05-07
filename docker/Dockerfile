# ─────────────── Stage 1 : build ───────────────
FROM python:3.11-slim AS builder
WORKDIR /opt/app

RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
        build-essential libyaml-dev      \
        libcairo2 libpango1.0-0 libpangoft2-1.0-0 \
        libharfbuzz0b libfreetype6 libgdk-pixbuf2.0-0 \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/tmp/wheels -r requirements.txt

# ─────────────── Stage 2 : runtime ─────────────
FROM python:3.11-slim
WORKDIR /opt/app

# WeasyPrint 런타임 의존 패키지
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq \
        libcairo2 libpango1.0-0 libpangoft2-1.0-0 \
        libharfbuzz0b libfreetype6 libgdk-pixbuf2.0-0 \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

# 파이썬 패키지 배포
COPY --from=builder /tmp/wheels /tmp/wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/tmp/wheels -r requirements.txt && \
    rm -rf /tmp/wheels

COPY . .
RUN chmod +x docker/entrypoint.sh
ENTRYPOINT ["bash", "docker/entrypoint.sh"]
