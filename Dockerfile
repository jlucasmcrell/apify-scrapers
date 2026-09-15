FROM python:3.11-slim

LABEL maintainer="Joseph McRell <https://github.com/jlucasmcrell>"
LABEL description="Apify Scrapers Model Context Protocol (MCP) Server"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY mcp_server.py .
COPY server.json .
COPY manifest.json .

ENTRYPOINT ["python", "mcp_server.py"]
