from workflows.base_workflow import BaseWorkflow

class EProceedingsWorkflow(BaseWorkflow):
    """Workflow to download E-Proceedings Excel"""
    
    def navigate_to_eproceedings(self):
        """Navigate: Pending Actions tab -> E Proceedings"""
        print("[INFO] Waiting for dashboard to load...")
        self.page.wait_for_timeout(5000)
        
        # Click Pending Actions tab
        print("[INFO] Looking for 'Pending Actions' tab...")
        pending_actions = self.page.query_selector('text=/.*pending.*action.*/i')
        if pending_actions:
            print("[INFO] Clicking Pending Actions tab")
            pending_actions.click()
            self.page.wait_for_timeout(2000)
        
        # Click E Proceedings from dropdown
        print("[INFO] Looking for 'E-Proceedings'...")
        eproceedings = self.page.query_selector('text="E-Proceedings"')
        if not eproceedings:
            eproceedings = self.page.query_selector('text=/.*e-proceeding.*/i')
        if eproceedings:
            print("[INFO] Clicking E-Proceedings")
            eproceedings.click()
            self.page.wait_for_timeout(3000)
    
    def download_excel(self):
        """Download Excel file"""
        print("[INFO] Looking for Excel Download button...")
        excel_btn = self.page.query_selector('button:has-text("Excel Download")')
        if not excel_btn:
            excel_btn = self.page.query_selector('button.downloadButtonsec')
        
        if excel_btn:
            print("[INFO] Clicking Excel Download button")
            with self.page.expect_download(timeout=30000) as dl:
                excel_btn.click()
            download = dl.value
            filename = f"{self.workflow_dir}/{download.suggested_filename}"
            download.save_as(filename)
            self.data.append({"file": filename, "type": "eproceedings"})
            print(f"[OK] Downloaded: {filename}")
        else:
            print("[ERROR] Excel Download button not found")
    
    def execute(self):
        """Main execution logic for E-Proceedings workflow"""
        self.navigate_to_eproceedings()
        self.download_excel()
        print(f"[OK] E-Proceedings download completed")
