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
| 08 | Extract links, forms, buttons, scripts | ⚠️ Links done, forms incomplete (action only), buttons/scripts extracted but not stored |
| 09 | Capture all browser requests and responses | ✅ Done |
| 10 | Store discovered pages, forms, links, network traffic in MongoDB | ⚠️ Links stored, requests/responses stored, forms not yet stored |
| 11 | Avoid duplicate links | ✅ Done — upsert on `scan_id + url` |
| 12 | Avoid duplicate forms | ❌ Not implemented |
| 13 | Avoid duplicate captured requests | ❌ No hash deduplication yet |
| 14 | Respect `allowed_domains` | ✅ Done |
| 15 | Respect `exclude_patterns` | ✅ Done |
| 16 | Support crawl depth limits (`max_depth`) | ✅ Done |
| 17 | Support maximum page limits (`max_pages`) | ✅ Done |
| 18 | Async crawling with `asyncio` and concurrency cap | ✅ Done — 3 concurrent workers |
| 19 | Allow graceful stop at any moment | ⚠️ Workers cancelled on browser close, partial state persisted |
| 20 | Resume from last saved state on re-run with same `scan_id` | ❌ RUNNING items not reset on restart |

---

## Done

### Infrastructure
- [x] `docker-compose.yml` — DVWA (port 8080) + MongoDB (port 27017)

### Configuration (`app/config.py`)
- [x] Single `CONFIG` dict — scan_id, login_url, start_url_after_login, allowed_domains
- [x] max_depth, max_pages, concurrency, login_steps, submit_selector
- [x] exclude_patterns, exact_exclude, skip_extensions

### Models (`app/models.py`)
- [x] `QueueItemStatus` — created / running / failed / completed
- [x] `ScanQueueItem`
- [x] `Link` — scan_id, url, depth, found_on
- [x] `Cookie`, `AuthState`
- [x] `PageRequest`, `PageResponse`

### Database (`app/db.py`)
- [x] MongoDB async connection via `motor`
- [x] Collections: `scan_queue`, `links`, `browser_requests`, `browser_responses`, `auth_state`, `error_log`
- [x] Scan queue: insert (upsert), pull next (atomic), update status, count
- [x] Links: insert with deduplication (upsert on `scan_id + url`)
- [x] Request / response insert helpers
- [x] Auth state insert and fetch helpers

### Login (`app/login.py`)
- [x] Config-driven form fill and submit
- [x] Waits for network idle after submit

### Login Verification (`app/login_validation.py`)
- [x] URL redirect check after login
- [x] Session cookie check (`PHPSESSID`, `session`, `token`)
- [x] Saves `AuthState` (success or failure) to MongoDB

### Request/Response Collection (`app/requests_responses.py`)
- [x] Hooks into Playwright `on("request")` and `on("response")`
- [x] Saves every network event to MongoDB during the session

### URL Scanning (`app/scan_url.py`)
- [x] Navigate to URL, check content-type (skip non-HTML)
- [x] Extract links — filter None, exact_exclude, exclude_patterns, external domains, skip_extensions
- [x] Normalize URLs — strip fragments, resolve relative to absolute with `urljoin`
- [x] Store each discovered link immediately to `links` collection
- [x] Enqueue links within depth limit, respecting max_pages
- [x] Extract forms, buttons, scripts (not yet stored to MongoDB)

### Worker (`app/worker.py`)
- [x] Pull next item atomically from `scan_queue`
- [x] Parse raw MongoDB dict into `ScanQueueItem`
- [x] Call `scan_url`, mark item as `completed` or `failed`
- [x] 3 concurrent workers via `asyncio.create_task`

### Orchestration (`app/main.py`)
- [x] Connect DB → launch browser → attach listeners → login → verify
- [x] Seed queue with `start_url_after_login` at depth 0
- [x] Launch worker pool (concurrency from config)
- [x] Cancel workers and close browser cleanly on disconnect

---

## To Do

### Resume Logic
- [ ] On startup, reset all `RUNNING` items to `CREATED` for the same `scan_id`

### Session Persistence
- [ ] Persist `storage_state` to disk and reuse on re-run

### Forms
- [ ] Full form extraction: action, method, fields (name/type/required), buttons
- [ ] Stable form hash for deduplication (`sha256` of page_url + action + method + fields)
- [ ] Store deduplicated forms to MongoDB (`forms` collection)
- [ ] Detect CSRF tokens in forms

### Request/Response Deduplication & Classification
- [ ] Hash each request (`sha256` of method + url + headers + body)
- [ ] Skip duplicate requests
- [ ] Classify requests: `is_api`, `is_static`

### Summary Output
- [ ] Print scan summary to console at end
- [ ] Store summary in MongoDB (`scans` collection)
