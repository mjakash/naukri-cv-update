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
        
        # We pin stealth_sync to V1 in requirements, so this works perfectly now
        stealth_sync(page)

        try:
            # 1. Go to the main homepage
            print("🚀 Navigating to Naukri Homepage...")
            page.goto("https://www.naukri.com/", wait_until="networkidle")

            # 2. Click the Login button on the top nav to open the side drawer
            print("🖱️ Opening login drawer...")
            page.click('#login_Layer')

            # 3. Define the selectors based on the actual HTML
            email_selector = 'input[placeholder="Enter your active Email ID / Username"]'
            password_selector = 'input[placeholder="Enter your password"]'
            
            # Wait for the drawer to slide out and the input to become visible
            page.wait_for_selector(email_selector, state="visible", timeout=10000)

            # 4. Human-like typing into the drawer inputs
            print("⌨️ Entering credentials...")
            page.type(email_selector, email, delay=100)
            page.type(password_selector, password, delay=120)
            
            # 5. Click Login inside the drawer
            page.click('button.loginButton[type="submit"]')
            
            # 6. Wait for Naukri to authenticate and route us to the profile dashboard
            print("⏳ Waiting for authentication...")
            page.wait_for_url("**/mnj/profile**", timeout=30000)
            print("🔓 Login Successful!")

            # 7. Direct file upload to the hidden input on the profile page
            print(f"📤 Uploading: {cv_filename}")
            page.set_input_files('input[type="file"]', cv_filename)
            
            # Allow time for Naukri's backend to process the file
            page.wait_for_timeout(7000)
            print("✅ Daily CV Update Complete!")

        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="debug_error.png", full_page=True)
            print("📸 Saved error screenshot to debug_error.png")
            import sys
            sys.exit(1)
            
        finally:
            browser.close()
            if os.path.exists(cv_filename):
                os.remove(cv_filename)