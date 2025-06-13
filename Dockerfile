FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

# Install sudo to fix permissions
RUN apt-get update && apt-get install -y sudo

# Allow botuser to run sudo without password
RUN echo "botuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /home/botuser/app
RUN chown botuser:botuser /home/botuser/app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER botuser

# Copy app files
COPY --chown=botuser:botuser . .

# Fix secret file permissions
RUN sudo chmod 644 /etc/secrets/*

# Use Render's PORT
ENV PORT=10000
EXPOSE $PORT

# Run the bot
CMD ["python", "main.py"]
