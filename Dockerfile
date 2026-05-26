FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY trading_bot ./trading_bot
COPY README.md .

ENTRYPOINT ["python", "-m", "trading_bot.cli"]
