FROM python:3.11-slim

# Create non-root user first
RUN useradd --create-home --shell /bin/bash botuser

# Set working directory with proper permissions
WORKDIR /home/botuser/app
RUN chown botuser:botuser /home/botuser/app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app as non-root user
USER botuser
COPY --chown=botuser:botuser . .

# Use Render's PORT variable
ENV PORT=10000
EXPOSE $PORT

# Run the bot
CMD ["python", "main.py"]
