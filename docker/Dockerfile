# ────────────────────────────────
# Stage 1 : build (wheel cache)
# ────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /opt/app

# C-extensions 빌드를 위한 툴체인 & WeasyPrint 컴파일 의존성
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential libyaml-dev \
        libcairo2 libpango1.0-0 libpangoft2-1.0-0 \
        libharfbuzz0b libfreetype6 libgdk-pixbuf2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/tmp/wheels -r requirements.txt

# ────────────────────────────────
# Stage 2 : runtime
# ────────────────────────────────
FROM python:3.11-slim
WORKDIR /opt/app

# ── WeasyPrint 런타임 + 한글 글꼴(Noto Sans CJK) ──
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libcairo2 libpango1.0-0 libpangoft2-1.0-0 \
        libharfbuzz0b libfreetype6 libgdk-pixbuf2.0-0 \
        fonts-noto-cjk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Python deps ───────────────────────────────────
COPY --from=builder /tmp/wheels /tmp/wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/tmp/wheels -r requirements.txt && \
    rm -rf /tmp/wheels

# ── 애플리케이션 코드 ─────────────────────────────
COPY . .
RUN chmod +x docker/entrypoint.sh

ENTRYPOINT ["bash", "docker/entrypoint.sh"]
