FROM python:3.11-slim
WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user EARLIER
RUN useradd --create-home --uid 1000 botuser
COPY --chown=botuser:botuser . .

USER botuser  # Switch before exposing ports

EXPOSE 10000
CMD ["python", "main.py"]
