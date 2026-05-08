# crawl-task

An authenticated web crawler built with Playwright that logs all browser requests and responses to MongoDB.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://github.com/astral-sh/uv)

## Start DVWA (frontend) and MongoDB

```bash
docker compose up -d
```

| Service | URL |
|---------|-----|
| DVWA | http://localhost:8080 |
| MongoDB | mongodb://localhost:27017 |

> First run only: go to http://localhost:8080/setup.php and click **Create / Reset Database**.

## Install dependencies

```bash
uv sync
uv run playwright install chromium
```

## Run the crawler

```bash
uv run python -m app.main
```

## Stop services

```bash
docker compose down
```

## Configuration

Edit `app/config.py` to change the target URL, login credentials, crawl depth, and other settings.
