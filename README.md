# Authenticated Browser Crawler & Network Capture Engine

A Python crawler that authenticates via a real browser, crawls the authenticated area, extracts links and forms, captures all network traffic, and stores everything in MongoDB. Built with Playwright, asyncio, and Motor.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [uv](https://github.com/astral-sh/uv)

---

## Quick Start

### 1. Start DVWA and MongoDB

```bash
docker compose up -d
```

| Service | URL |
|---------|-----|
| DVWA | http://localhost:8080 |
| MongoDB | mongodb://localhost:27017 |

> First run only: go to http://localhost:8080/setup.php and click **Create / Reset Database**.

### 2. Install dependencies

```bash
uv sync
uv run playwright install chromium
```

### 3. Run the crawler

```bash
uv run python -m app.main
```

### 4. Stop services

```bash
docker compose down
```

---

## Configuration

All parameters are hardcoded in `app/config.py`:

```python
CONFIG = {
    "scan_id": "scan_123",
    "login_url": "http://localhost:8080/login.php",
    "start_url_after_login": "http://localhost:8080/index.php",
    "allowed_domains": ["localhost:8080"],
    "max_depth": 3,
    "max_pages": 100,
    "concurrency": 3,
    "login_steps": [
        {"selector": "[name='username']", "value": "admin"},
        {"selector": "[name='password']", "value": "password"}
    ],
    "submit_selector": "[name='Login'][type='submit']",
    "exclude_patterns": ["logout", "delete", "remove"],
    "exact_exclude": ["#", "."],
    "skip_extensions": [".pdf", ".md", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".zip", ".yml", ".yaml", ".dist"]
}
```

| Field | Description |
|-------|-------------|
| `scan_id` | Unique identifier for the scan session — used for resume |
| `login_url` | URL of the login page |
| `start_url_after_login` | Seed URL to begin crawling after login |
| `allowed_domains` | Only crawl URLs within these domains |
| `max_depth` | Maximum crawl depth from the seed URL |
| `max_pages` | Maximum number of pages to enqueue |
| `concurrency` | Number of parallel worker tasks |
| `login_steps` | List of `{selector, value}` pairs to fill the login form |
| `submit_selector` | Selector of the login submit button |
| `exclude_patterns` | Skip URLs containing any of these substrings |
| `exact_exclude` | Skip links that exactly match these values |
| `skip_extensions` | Skip links ending with these file extensions |

---

## Project Structure

```
app/
  main.py                        # Entry point — login, workers, shutdown
  config.py                      # Hardcoded configuration
  models.py                      # Pydantic data models
  auth/
    login.py                     # Config-driven login form fill and submit
    validation.py                # Login success validation, saves AuthState to MongoDB
  capture/
    requests_responses.py        # Playwright network event capture
  crawler/
    worker.py                    # Async worker — pulls from queue, calls scan_url
    scan_url.py                  # Page scanning — links, forms, scripts
  db/
    connection.py                # MongoDB connection
    queue.py                     # Scan queue CRUD
    links.py                     # Links collection
    forms.py                     # Forms collection
    requests.py                  # Requests, responses, auth state
```

---

## MongoDB Schema

### `scan_queue`
Per-URL work items. Workers pull atomically using `findOneAndUpdate`.

| Field | Description |
|-------|-------------|
| `id` | Unique item ID |
| `url_name` | URL to scan |
| `depth` | Crawl depth |
| `status` | `created` → `running` → `completed` / `failed` |
| `scanned_by` | Worker ID that processed it |
| `scanned_at` | Timestamp of completion |

### `links`
All unique discovered links, deduplicated by `scan_id + url`.

| Field | Description |
|-------|-------------|
| `scan_id` | Scan session ID |
| `url` | Normalized absolute URL |
| `depth` | Depth at which it was found |
| `found_on` | Page URL where the link was discovered |

### `forms`
Unique forms deduplicated by `scan_id + form_hash`.

| Field | Description |
|-------|-------------|
| `scan_id` | Scan session ID |
| `page_url` | Page where the form was found |
| `form_hash` | `sha256` of page_url + action + method + sorted fields |
| `action` | Form action URL |
| `method` | `GET` or `POST` |
| `fields` | List of `{name, type, required}` |
| `buttons` | List of button texts |
| `csrf_detected` | Whether a CSRF token field was detected |

### `browser_requests` / `browser_responses`
All network traffic captured during the browser session.

### `auth_state`
Login result — success/failure, session cookies.

---

## Resume Mechanism

The crawler is fully resumable using `scan_id` as the session key:

- Every discovered URL is inserted into `scan_queue` with `status: created`
- Workers claim items atomically by setting `status: running`
- On completion, status is updated to `completed` or `failed`
- **On startup**, any items stuck in `running` from a previous interrupted run are automatically reset to `created`
- Re-running with the same `scan_id` continues from where it stopped — already completed URLs are skipped via upsert deduplication

To start a fresh scan, change `scan_id` in `config.py`.

---

## Graceful Shutdown

Press `Ctrl+C` to stop the crawler cleanly:

1. Workers stop picking up new URLs
2. Each worker finishes its current page scan
3. Any items still in `running` state are reset to `created`
4. Browser and MongoDB connection are closed cleanly

Partial state is always consistent and resumable.
