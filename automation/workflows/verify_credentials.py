
from workflows.base_workflow import BaseWorkflow

class VerifyCredentialsWorkflow(BaseWorkflow):
    """Workflow to just verify credentials by logging in"""
    
    def execute(self):
        """
        Login and scrape user details (Name) if possible.
        """
        import json
        
        try:
            self.login()
            
            # Attempt to scrape name
            print("[INFO] Attempting to scrape user name...")
            user_name = None
            
            # Common selectors for name in ITR portal (subject to change)
            # 1. Dashboard welcome message
            # 2. Profile menu text
            # 3. User profile page
            
            # Try finding an element with "Welcome" or the profile icon text
            try:
                # Wait for dashboard to settle
                self.page.wait_for_timeout(3000)
                
                # Check for "Welcome" text variants
                welcome_el = self.page.query_selector('text=/Welcome.*/i')
                if welcome_el:
                    text = welcome_el.inner_text()
                    # Extract name from "Welcome X"
                    user_name = text.replace("Welcome", "").strip().split('\n')[0].strip()
                
                if not user_name:
                    # Try profile icon/text
                    pass

            except Exception as e:
                print(f"[WARNING] Failed to scrape name: {e}")
            
            result = {
                "status": "success",
                "name": user_name
            }
            print(f"[DATA] {json.dumps(result)}")
            
            # Add to self.data so it gets written to results.json
            self.data.append(result)
            
        except Exception as e:
             # Login failed or other error
             print(f"[ERROR] Verification failed: {e}")
             # We rely on BaseWorkflow to handle severe errors, but here we print JSON for failure
             print(f"[DATA] {json.dumps({'status': 'error', 'message': str(e)})}")
             raise e
