from workflows.base_workflow import BaseWorkflow

class AISDownloadWorkflow(BaseWorkflow):
    """Workflow to download AIS/TIS"""
    
    def navigate_to_ais(self):
        """Navigate to AIS tab"""
        print("[INFO] Waiting for dashboard to load...")
        self.page.wait_for_timeout(5000)
        
        # Click AIS tab
        print("[INFO] Looking for 'AIS' tab...")
        ais_tab = self.page.query_selector('text=/.*AIS.*/i')
        if ais_tab:
            print("[INFO] Clicking AIS tab")
            with self.page.context.expect_page() as new_page_info:
                ais_tab.click()
            self.page = new_page_info.value
            print("[INFO] Switched to AIS tab")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(3000)
    
    def download_ais(self):
        """Download AIS/TIS file"""
        print("[INFO] Looking for Download AIS/TIS button...")
        self.page.wait_for_timeout(3000)
        
        # Check for error modal (has error text) and close it
        error_modal = self.page.query_selector('text=/.*error.*/i, text=/.*failed.*/i')
        if error_modal:
            print("[INFO] Error modal detected, closing...")
            close_button = self.page.query_selector('button:has-text("OK"), button:has-text("Close")')
            if close_button:
                close_button.click()
                self.page.wait_for_timeout(2000)
        
        # Try multiple selectors
        download_btn = self.page.query_selector('button:has-text("Download AIS/TIS")')
        if not download_btn:
            download_btn = self.page.query_selector('button.download-btn-padding')
        if not download_btn:
            download_btn = self.page.query_selector('button:has-text("Download")')
        
        if download_btn:
            print("[INFO] Clicking Download AIS/TIS button")
            download_btn.click()
            self.page.wait_for_timeout(3000)
            
            # Click the second download button in modal
            print("[INFO] Looking for download buttons in modal...")
            download_buttons = self.page.query_selector_all('button.btn-outline-primary')
            print(f"[DEBUG] Found {len(download_buttons)} buttons")
            
            if len(download_buttons) >= 2:
                print("[INFO] Clicking second download button (JSON)")
                download_buttons[1].click()
                self.page.wait_for_timeout(3000)
                
                # Handle CAPTCHA and get download
                print("[INFO] Checking for CAPTCHA...")
                download_result = self.handle_captcha_if_present()
                if download_result and hasattr(download_result, 'suggested_filename'):
                    print("[INFO] CAPTCHA handled, saving download...")
                    filename = f"{self.workflow_dir}/{download_result.suggested_filename}"
                    download_result.save_as(filename)
                    self.data.append({"file": filename, "type": "ais_tis"})
                    print(f"[OK] Downloaded: {filename}")
                else:
                    print("[ERROR] Download not received")
            else:
                print(f"[ERROR] Expected 3 buttons, found {len(download_buttons)}")
        else:
            print("[ERROR] Download AIS/TIS button not found")
            print(f"[DEBUG] Current URL: {self.page.url}")
    
    def execute(self):
        """Main execution logic for AIS download workflow"""
        self.navigate_to_ais()
        self.download_ais()
        print(f"[OK] AIS/TIS download completed")
