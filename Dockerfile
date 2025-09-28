ARG python_version=3.13-slim

FROM python:$python_version AS builder
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/

ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy

# Install project dependencies with build tools available
WORKDIR /opt/monsteras
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-group dev

# -------------------------------------------------------------------------------

FROM python:$python_version

ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies from build cache
# .venv not put in /app so that it doesn't conflict with the dev
# volume we use to avoid rebuilding image every code change locally
COPY --from=builder /opt/monsteras/.venv /opt/monsteras/.venv

# Copy the source code in last to optimize rebuilding the image
WORKDIR /app
COPY . .
ENV PATH="/opt/monsteras/.venv/bin:$PATH"

ENTRYPOINT ["python"]
CMD ["src/main.py"]
