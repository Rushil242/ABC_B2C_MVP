from workflows.base_workflow import BaseWorkflow
import config

class FiledReturnsWorkflow(BaseWorkflow):
    """Workflow to download all filed income tax returns as JSON"""
    
    def navigate_to_filed_returns(self):
        """Navigate to View Filed Returns page"""
        print("[INFO] Waiting for dashboard to load...")
        self.page.wait_for_timeout(5000)
        
        # Click e-file menu
        print("[INFO] Looking for 'e-file' menu...")
        efile_menu = self.page.query_selector('text=/.*e-file.*/i')
        if efile_menu:
            print("[INFO] Clicking e-file menu")
            efile_menu.click()
            self.page.wait_for_timeout(1500)
        
        # Hover over Income Tax Returns
        print("[INFO] Looking for 'income tax returns' in dropdown...")
        itr_menu = self.page.query_selector('.cdk-overlay-container >> text=/.*income tax return.*/i')
        if itr_menu:
            print("[INFO] Hovering over income tax returns")
            itr_menu.hover(force=True)
            self.page.wait_for_timeout(1500)
        
        # Click View Filed Returns
        print("[INFO] Looking for 'view filed returns' in submenu...")
        view_returns = self.page.query_selector('.cdk-overlay-container >> text=/.*view.*filed.*return.*/i')
        if view_returns:
            print("[INFO] Clicking view filed returns")
            view_returns.click(force=True)
            self.page.wait_for_timeout(3000)
    
    def download_json_from_page(self, page_num):
        """Download all JSON files from current page"""
        # Scroll through page
        last_height = self.page.evaluate("document.body.scrollHeight")
        scroll_position = 0
        scroll_step = 500
        
        while scroll_position < last_height:
            self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
            self.page.wait_for_timeout(300)
            scroll_position += scroll_step
            new_height = self.page.evaluate("document.body.scrollHeight")
            if new_height > last_height:
                last_height = new_height
        
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(1000)
        
        # Find unique Download JSON buttons
        json_buttons = self.page.query_selector_all('button:has-text("Download JSON"), a:has-text("Download JSON")')
        seen_positions = set()
        unique_buttons = []
        
        for btn in json_buttons:
            box = btn.bounding_box()
            if box:
                pos = (round(box['x']), round(box['y']))
                if pos not in seen_positions:
                    seen_positions.add(pos)
                    unique_buttons.append(btn)
        
        print(f"[INFO] Found {len(unique_buttons)} buttons on page {page_num}")
        
        # Download from each button
        downloaded = 0
        for button in unique_buttons:
            try:
                button.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                with self.page.expect_download(timeout=10000) as dl:
                    button.click()
                download = dl.value
                filename = f"{self.workflow_dir}/return_{len(self.data)+1}_{download.suggested_filename}"
                download.save_as(filename)
                self.data.append({"file": filename, "page": page_num})
                downloaded += 1
                print(f"  [OK] Downloaded: {filename}")
            except Exception as e:
                print(f"  [ERROR] Download failed: {e}")
        
        return downloaded
    
    def has_next_page(self):
        """Check if next page button exists and is enabled"""
        next_button = self.page.query_selector('img[alt="next page"]')
        if next_button:
            src = next_button.get_attribute('src') or ''
            return 'nextPageEnable' in src
        return False
    
    def go_to_next_page(self):
        """Click next page button"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)
        
        next_button = self.page.query_selector('img[alt="next page"]')
        if next_button:
            next_button.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            next_button.click(force=True)
            self.page.wait_for_timeout(3000)
            return True
        return False
    
    def execute(self):
        """Main execution logic for filed returns workflow"""
        self.navigate_to_filed_returns()
        
        print("[INFO] Starting pagination loop...")
        page_num = 1
        
        while True:
            print(f"[INFO] Processing page {page_num}...")
            self.download_json_from_page(page_num)
            
            if self.has_next_page():
                print(f"[INFO] Moving to page {page_num + 1}...")
                if self.go_to_next_page():
                    page_num += 1
                else:
                    print(f"[INFO] Failed to navigate. Completed {page_num} pages.")
                    break
            else:
                print(f"[INFO] No more pages. Completed {page_num} pages.")
                break
        
        print(f"[OK] Total downloads: {len(self.data)}")
