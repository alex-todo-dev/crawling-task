from app.config import CONFIG

async def login(page):
    login_steps = CONFIG['login_steps']
   
    # Input user data    
    for step in login_steps:
        await page.fill(step['selector'], step['value'])

    # Submit user/password
    await page.click(CONFIG["submit_selector"])
    await page.wait_for_load_state("networkidle")                                                                  
    print("URL after login:", page.url)