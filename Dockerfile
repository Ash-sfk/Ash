FROM python:3.11-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY . .

# Create a non-root user and set permissions
RUN useradd --create-home --uid 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Expose port (required by Render)
EXPOSE 10000

# Command to run the bot
CMD ["python", "main.py"]
