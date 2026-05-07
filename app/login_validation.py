async def login_verification(page, expected_url):
     # Check if the url is the same as the start_url_after_login
    if page.url != expected_url:
        print("Login failed. Not on exppected page after login")
        return

    # Check coockies if PHP session id exists
    cookies = await page.context.cookies()
    session = any(c["name"] in ("PHPSESSID") for c in cookies)
    print(f"LOGIN VERFICITATION: {cookies}")
    if not session:                                                                                           
        print("Login failed: no session cookie")
        return False  
    
    return {"Login": "Success"}
