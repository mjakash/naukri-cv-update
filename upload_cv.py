import shutil
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def prepare_cv():
    base_cv_path = "./base_cv.pdf"
    if not os.path.exists(base_cv_path):
        raise FileNotFoundError("Base CV not found in root.")

    now = datetime.now()
    todays_date_str = f"{now.day}{now.strftime('%b').upper()}"
    new_cv_path = f"./manirujjamanAkashCV_SDET_{todays_date_str}.pdf"
    
    shutil.copy(base_cv_path, new_cv_path)
    print(f"✅ Generated: {new_cv_path}")
    return new_cv_path

def upload_to_naukri(cv_filename):
    # Fetch credentials from GitHub Secrets
    email = os.environ.get("NAUKRI_EMAIL")
    password = os.environ.get("NAUKRI_PASSWORD")

    if not email or not password:
        raise ValueError("Missing NAUKRI_EMAIL or NAUKRI_PASSWORD environment variables")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)

        try:
            print("🚀 Navigating to Login...")
            page.goto("https://www.naukri.com/nlogin/login", wait_until="networkidle")

            # Human-like typing: types with random delays between 50ms and 150ms
            page.type("#usernameField", email, delay=100)
            page.type("#passwordField", password, delay=120)
            
            # Click Login
            page.click('button[type="submit"]')
            
            # Wait for profile page to load
            page.wait_for_url("**/mnj/profile**", timeout=30000)
            print("🔓 Login Successful!")

            # Direct file upload to the hidden input
            print(f"📤 Uploading: {cv_filename}")
            page.set_input_files('input[type="file"]', cv_filename)
            
            # Allow time for upload to complete
            page.wait_for_timeout(7000)
            print("✅ Daily CV Update Complete!")

        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="debug_error.png")
        finally:
            browser.close()
            if os.path.exists(cv_filename):
                os.remove(cv_filename)

if __name__ == "__main__":
    path = prepare_cv()
    upload_to_naukri(path)