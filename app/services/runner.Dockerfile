# app/services/runner.Dockerfile
FROM python:3.11-slim

# minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install test deps
# Keep versions simple; pytest-json-report is required for JSON output.
RUN python -m pip install --upgrade pip
RUN pip install pytest pytest-json-report

# Create an unprivileged user (safer)
RUN useradd --create-home runner
USER runner
ENV HOME=/home/runner
WORKDIR /workspace

# Entrypoint left to the container command
CMD ["bash", "-lc", "pytest -q --json-report --json-report-file=report.json"]
