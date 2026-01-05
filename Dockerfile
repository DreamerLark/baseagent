FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .
COPY skills.py .
COPY mcp_client.py .
COPY server.py .
COPY .env.example .

ENV PORT=8000

EXPOSE 8000

CMD ["python", "server.py"]
