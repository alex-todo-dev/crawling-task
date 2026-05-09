# Project Progress

## Requirements Coverage

| # | Requirement | Status |
|---|-------------|--------|
| 01 | Open a real browser using Playwright (Chromium) | ✅ Done |
| 02 | Navigate to the login page | ✅ Done |
| 03 | Fill all fields from `login_steps` | ✅ Done |
| 04 | Click `submit_selector` | ✅ Done |
| 05 | Validate login success | ✅ Done |
| 06 | Save authenticated browser storage / session state | ⚠️ Cookies saved to MongoDB, `storage_state` not persisted for reuse across runs |
| 07 | Start crawling from `start_url_after_login` | ✅ Done |
| 08 | Extract links, forms, buttons, scripts | ✅ Done — links, forms (fields/buttons/csrf), scripts extracted and stored |
| 09 | Capture all browser requests and responses | ✅ Done |
| 10 | Store discovered pages, forms, links, network traffic in MongoDB | ✅ Done — links, forms, requests/responses all stored |
| 11 | Avoid duplicate links | ✅ Done — upsert on `scan_id + url` |
| 12 | Avoid duplicate forms | ✅ Done — upsert on `scan_id + form_hash` |
| 13 | Avoid duplicate captured requests | ❌ No hash deduplication yet |
| 14 | Respect `allowed_domains` | ✅ Done |
| 15 | Respect `exclude_patterns` | ✅ Done |
| 16 | Support crawl depth limits (`max_depth`) | ✅ Done |
| 17 | Support maximum page limits (`max_pages`) | ✅ Done |
| 18 | Async crawling with `asyncio` and concurrency cap | ✅ Done — 3 concurrent workers |
| 19 | Allow graceful stop at any moment | ✅ Done — SIGINT/SIGTERM handled, workers finish current scan then stop |
| 20 | Resume from last saved state on re-run with same `scan_id` | ✅ Done — RUNNING items reset to CREATED on startup |

---

## Done

### Infrastructure
- [x] `docker-compose.yml` — DVWA (port 8080) + MongoDB (port 27017)

### Configuration (`app/config.py`)
- [x] Single `CONFIG` dict — scan_id, login_url, start_url_after_login, allowed_domains
- [x] max_depth, max_pages, concurrency, login_steps, submit_selector
- [x] exclude_patterns, exact_exclude, skip_extensions

### Project Structure
- [x] `app/db/` — connection.py, queue.py, links.py, forms.py, requests.py
- [x] `app/crawler/` — worker.py, scan_url.py
- [x] `app/auth/` — login.py, validation.py
- [x] `app/capture/` — requests_responses.py

### Models (`app/models.py`)
- [x] `QueueItemStatus` — created / running / failed / completed
- [x] `ScanQueueItem`
- [x] `Link` — scan_id, url, depth, found_on
- [x] `FormField` — name, type, required
- [x] `Form` — scan_id, page_url, form_hash, action, method, fields, buttons, csrf_detected
- [x] `Cookie`, `AuthState`
- [x] `PageRequest`, `PageResponse`

### Database (`app/db/`)
- [x] `connection.py` — async MongoDB connection, collection name constants
- [x] `queue.py` — insert, pull next (atomic), update status, count, reset running items
- [x] `links.py` — insert with deduplication (upsert on `scan_id + url`)
- [x] `forms.py` — insert with deduplication (upsert on `scan_id + form_hash`)
- [x] `requests.py` — insert request/response, insert/get auth state

### Auth (`app/auth/`)
- [x] `login.py` — config-driven form fill and submit, waits for network idle
- [x] `validation.py` — URL redirect check, session cookie check, saves AuthState to MongoDB

### Capture (`app/capture/`)
- [x] `requests_responses.py` — hooks into Playwright network events, saves to MongoDB

### Crawler (`app/crawler/`)
- [x] `scan_url.py` — navigate, content-type check, extract and filter links, extract forms with full field data, CSRF detection, stable hash, store all to MongoDB immediately on discovery
- [x] `worker.py` — pull next item atomically, parse into ScanQueueItem, call scan_url, update status, respects shutdown event

### Orchestration (`app/main.py`)
- [x] Connect DB → launch browser → attach listeners → login → verify
- [x] Reset RUNNING items on startup for resume
- [x] Seed queue with `start_url_after_login` at depth 0
- [x] Launch worker pool (concurrency from config)
- [x] SIGINT/SIGTERM graceful shutdown — workers finish current scan, RUNNING items reset, DB closed cleanly

---

## To Do

### Session Persistence
- [ ] Persist `storage_state` to disk and reuse on re-run

### Request/Response Deduplication & Classification
- [ ] Hash each request (`sha256` of method + url + headers + body)
- [ ] Skip duplicate requests
- [ ] Classify requests: `is_api`, `is_static`

### Summary Output
- [ ] Print scan summary to console at end
- [ ] Store summary in MongoDB (`scans` collection)
