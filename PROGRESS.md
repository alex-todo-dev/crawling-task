# Project Progress

## Done

### Infrastructure
- [x] `docker-compose.yml` — DVWA (port 8080) + MongoDB (port 27017)

### Database (`app/db.py`)
- [x] MongoDB async connection via `motor`
- [x] Collections: `scan_queue`, `browser_requests`, `browser_responses`, `auth_state`
- [x] Scan queue CRUD: insert, update status, pull next item
- [x] Request / response insert helpers
- [x] Auth state insert and fetch helpers
- [x] `QueueItemStatus` enum: `created → running → failed → completed`

### Models (`app/models.py`)
- [x] `Cookie`
- [x] `AuthState`
- [x] `PageRequest`
- [x] `PageResponse`

### Login (`app/login.py`)
- [x] Config-driven form fill and submit
- [x] Waits for network idle after submit

### Login Verification (`app/login_validation.py`)
- [x] URL check after login
- [x] Session cookie check (`PHPSESSID`, `session`, `token`)
- [x] Saves `AuthState` (success or failure) to MongoDB

### Request/Response Collection (`app/requests_responses.py`)
- [x] Hooks into Playwright `on("request")` and `on("response")`
- [x] Saves every network event to MongoDB during the session

### Orchestration (`app/main.py`)
- [x] Connect DB → launch browser → attach listeners → navigate → login → verify → wait for close

---

## To Do

### URL Scanning (`app/scan_url.py`)
- [ ] Navigate to a given URL with Playwright
- [ ] Extract all links from the page
- [ ] Filter by allowed domains and exclude patterns
- [ ] Respect max depth

### Worker (`app/worker.py`)
- [ ] Pull next item from `scan_queue`
- [ ] Mark item as `running`, call `scan_url`, mark as `completed` or `failed`
- [ ] Seed the queue with the start URL after login
- [ ] Run multiple workers concurrently (see `concurrency` in config)

### Crawl Loop (`app/main.py`)
- [ ] Seed queue with `start_url_after_login` after successful login
- [ ] Launch worker pool
- [ ] Stop when queue is empty or `max_pages` is reached
