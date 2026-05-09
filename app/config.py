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


