from playwright.sync_api import sync_playwright, Page
from pathlib import Path
import json
import config

class BaseWorkflow:
    """Base class for all income tax website workflows"""
    
    def __init__(self, headless=False):
        self.pw = None
        self.browser = None
        self.page = None
        self.data = []
        self.workflow_dir = None
        self.headless = headless
    
    def initialize_browser(self):
        """Setup browser with anti-detection"""
        # Create workflow-specific directory
        workflow_name = self.__class__.__name__.replace('Workflow', '').lower()
        self.workflow_dir = f"{config.DOWNLOAD_PATH}/{workflow_name}"
        Path(self.workflow_dir).mkdir(parents=True, exist_ok=True)
        
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        context = self.browser.new_context(
            accept_downloads=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = {runtime: {}};
        """)
        self.page = context.new_page()
        print(f"[OK] Browser initialized, output: {self.workflow_dir}")
    
    def login(self):
        """Login to income tax portal"""
        print(f"[INFO] Navigating to {config.BASE_URL}")
        self.page.goto(config.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        
        print("[INFO] Analyzing page for login fields...")
        
        # Pre-step: Check if we need to click "Login" button (common on homepage)
        login_button = self.page.query_selector('a:has-text("Login"), button:has-text("Login")')
        if login_button and login_button.is_visible():
            print("[INFO] Found Login button, clicking...")
            login_button.click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)

        # Step 1: Enter username/PAN
        all_inputs = self.page.query_selector_all('input')
        username_field = None
        for inp in all_inputs:
            input_type = inp.get_attribute('type') or 'text'
            input_name = inp.get_attribute('name') or ''
            input_id = inp.get_attribute('id') or ''
            input_placeholder = inp.get_attribute('placeholder') or ''
            text = f"{input_name} {input_id} {input_placeholder}".lower()
            
            if input_type in ['text', 'email'] and any(keyword in text for keyword in ['user', 'login', 'email', 'pan', 'id', 'aadhaar']):
                username_field = inp
                break
        
        if not username_field:
            raise Exception("Username field not found")
        
        print(f"[INFO] Filling username: {config.USERNAME}")
        username_field.fill(config.USERNAME)
        self.page.wait_for_timeout(1000)
        
        # Click Continue
        all_buttons = self.page.query_selector_all('button, input[type="submit"]')
        continue_button = None
        for btn in all_buttons:
            btn_text = (btn.inner_text() or '').lower()
            if any(word in btn_text for word in ['continue', 'next', 'proceed']):
                continue_button = btn
                break
        
        if continue_button:
            continue_button.click()
            self.page.wait_for_timeout(2000)
        else:
            self.page.keyboard.press('Enter')
            self.page.wait_for_timeout(2000)
        
        # Step 2: Enter password
        print("[INFO] Looking for password field...")
        password_field = self.page.query_selector('input[type="password"]')
        if not password_field:
            raise Exception("Password field not found")
        
        print("[INFO] Filling password")
        password_field.fill(config.PASSWORD)
        self.page.wait_for_timeout(1000)
        
        # Check for checkboxes
        checkboxes = self.page.query_selector_all('input[type="checkbox"]')
        if checkboxes:
            for checkbox in checkboxes:
                try:
                    if not checkbox.is_checked():
                        checkbox.click(force=True)
                except:
                    pass
            self.page.wait_for_timeout(1000)
        
        # Click Continue
        all_buttons = self.page.query_selector_all('button, input[type="submit"], a.btn, [role="button"]')
        continue_button = None
        for btn in all_buttons:
            try:
                btn_text = (btn.inner_text() or '').lower()
                if 'continue' in btn_text:
                    continue_button = btn
                    break
            except:
                pass
        
        if continue_button:
            self.page.wait_for_timeout(500)
            continue_button.click()
        else:
            raise Exception("Continue button not found")
        
        self.page.wait_for_timeout(3000)
        
        # Handle session modal
        modal_text = self.page.query_selector('text=/.*session.*active.*/i')
        if modal_text:
            print("[INFO] Session modal detected")
            all_buttons = self.page.query_selector_all('button')
            for btn in all_buttons:
                try:
                    btn_text = (btn.inner_text() or '').lower()
                    if 'login' in btn_text and 'here' in btn_text:
                        btn.click(force=True)
                        print("[INFO] Clicked 'Login Here' button")
                        self.page.wait_for_timeout(3000)
                        break
                except:
                    pass
        
        print("[OK] Login completed")
    
    def execute(self):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def cleanup(self):
        """Save results and close browser"""
        output_file = f"{self.workflow_dir}/results.json"
        with open(output_file, "w") as f:
            json.dump(self.data, f, indent=2)
        print(f"[OK] Downloaded {len(self.data)} files")
        print(f"[OK] Results saved to {output_file}")
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()
    
    def run(self):
        """Main workflow execution"""
        try:
            self.initialize_browser()
            self.login()
            self.execute()
        except Exception as e:
            # Handle potential encoding errors in Windows terminals
            try:
                print(f"[ERROR] Workflow failed: {e}")
            except UnicodeEncodeError:
                print(f"[ERROR] Workflow failed: {e}".encode("utf-8", errors="ignore").decode("utf-8"))
            
            # Capture screenshot on failure
            if self.page:
                try:
                    screenshot_path = f"{self.workflow_dir}/error_screenshot.png"
                    self.page.screenshot(path=screenshot_path)
                    print(f"[INFO] Error screenshot saved to {screenshot_path}")
                except Exception as se:
                    print(f"[ERROR] Failed to save screenshot: {se}")

            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
