from app.models import AuthState, Cookie
from app.config import CONFIG
from app.db.requests import insert_auth_state

async def login_verification(page, expected_url, db) -> None:
    cookies = await page.context.cookies()

    if page.url != expected_url:
        print("Login failed. Not on expected page after login")
        auth_state = AuthState(
            scan_id=CONFIG["scan_id"],
            login_url=CONFIG["login_url"],
            success=False,
            cookies=[],
        )
        await insert_auth_state(db, auth_state)
        return

    session = any(c["name"] in ("PHPSESSID", "session", "token") for c in cookies)
    print(f"LOGIN VERIFICATION: {cookies}")

    if not session:
        print("Login failed: no session cookie")
        auth_state = AuthState(
            scan_id=CONFIG["scan_id"],
            login_url=CONFIG["login_url"],
            success=False,
            cookies=[],
        )
        await insert_auth_state(db, auth_state)
        return

    cookie_models = [
        Cookie(
            name=c["name"],
            value=c["value"],
            domain=c["domain"],
            path=c["path"],
            expires=c.get("expires"),
            http_only=c.get("httpOnly", False),
            secure=c.get("secure", False),
        )
        for c in cookies
    ]

    auth_state = AuthState(
        scan_id=CONFIG["scan_id"],
        login_url=CONFIG["login_url"],
        success=True,
        cookies=cookie_models,
    )
    await insert_auth_state(db, auth_state)
    print(f"Auth state saved: success={auth_state.success}")
