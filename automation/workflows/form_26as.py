from workflows.base_workflow import BaseWorkflow

class Form26ASWorkflow(BaseWorkflow):
    """Workflow to export Form 26AS as PDF"""
    
    def navigate_to_form_26as(self):
        """Navigate: e-File tab -> Income Tax Returns -> View Form 26AS -> Handle modal -> View Tax Credit"""
        print("[INFO] Waiting for dashboard to load...")
        self.page.wait_for_timeout(5000)
        
        # Click e-File tab
        print("[INFO] Looking for 'e-File' tab...")
        efile_tab = self.page.query_selector('text=/.*e-file.*/i')
        if efile_tab:
            print("[INFO] Clicking e-File tab")
            efile_tab.click()
            self.page.wait_for_timeout(1500)
        
        # Hover over Income Tax Returns
        print("[INFO] Looking for 'Income Tax Returns'...")
        itr_menu = self.page.query_selector('.cdk-overlay-container >> text=/.*income tax return.*/i')
        if itr_menu:
            print("[INFO] Hovering over Income Tax Returns")
            itr_menu.hover(force=True)
            self.page.wait_for_timeout(1500)
        
        # Click View Form 26AS
        print("[INFO] Looking for 'View Form 26AS'...")
        form_26as = self.page.query_selector('.cdk-overlay-container >> text=/.*view.*form.*26as.*/i')
        if form_26as:
            print("[INFO] Clicking View Form 26AS")
            with self.page.context.expect_page() as new_page_info:
                form_26as.click(force=True)
            self.page = new_page_info.value
            print("[INFO] Switched to new tab")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(3000)
        
        # Handle checkbox modal
        print("[INFO] Checking for modal checkbox...")
        checkbox = self.page.query_selector('#Details')
        if checkbox:
            print("[INFO] Modal detected, ticking checkbox")
            checkbox.click(force=True)
            self.page.wait_for_timeout(1000)
            
            proceed_button = self.page.query_selector('#btn')
            if proceed_button:
                print("[INFO] Clicking Proceed button")
                proceed_button.click(force=True)
                self.page.wait_for_timeout(3000)
            else:
                print("[ERROR] Proceed button not found")
        else:
            print("[WARNING] Modal checkbox not found, continuing...")
        
        # Click View Tax Credit
        print("[INFO] Looking for 'View Tax Credit'...")
        self.page.wait_for_timeout(3000)
        
        # Try multiple selectors
        tax_credit = self.page.query_selector('a[href="/serv/tapn/view26AS.xhtml"]')
        if not tax_credit:
            tax_credit = self.page.query_selector('text="View Tax Credit (Form 26AS/Annual Tax Statement)"')
        if not tax_credit:
            tax_credit = self.page.query_selector('a:has-text("View Tax Credit")')
        
        if tax_credit:
            print("[INFO] Clicking View Tax Credit")
            self.page.evaluate('window.location.href = "/serv/tapn/view26AS.xhtml"')
            self.page.wait_for_timeout(3000)
        else:
            print("[ERROR] View Tax Credit link not found")
    
    def export_pdf(self):
        """Export Form 26AS as PDF for all assessment years"""
        print("[INFO] Looking for format dropdown...")
        format_dropdown = self.page.query_selector('#viewType')
        if format_dropdown:
            print("[INFO] Selecting HTML format")
            self.page.select_option('#viewType', 'HTML')
            self.page.wait_for_timeout(1000)
        
        print("[INFO] Looking for Assessment Year dropdown...")
        dropdown = self.page.query_selector('#AssessmentYearDropDown')
        
        if not dropdown:
            print("[ERROR] Assessment Year dropdown not found")
            return
        
        # Get all options except the first one (--Select--)
        options = self.page.query_selector_all('#AssessmentYearDropDown option')
        years = []
        for option in options:
            value = option.get_attribute('value')
            if value and value != '':
                years.append(value)
        
        print(f"[INFO] Found {len(years)} assessment years")
        
        # Loop through each year
        for year in years:
            print(f"[INFO] Processing year {year}...")
            
            # Select the year
            self.page.select_option('#AssessmentYearDropDown', year)
            self.page.wait_for_timeout(2000)
            
            # Click View / Download button
            view_button = self.page.query_selector('#btnSubmit')
            if view_button:
                print(f"[INFO] Clicking View / Download for year {year}")
                view_button.click()
                self.page.wait_for_timeout(3000)
            
            # Click Export as PDF
            pdf_button = self.page.query_selector('#pdfBtn')
            if pdf_button:
                print(f"[INFO] Clicking Export as PDF for year {year}")
                with self.page.expect_download(timeout=30000) as dl:
                    pdf_button.click()
                download = dl.value
                filename = f"{self.workflow_dir}/{year}_{download.suggested_filename}"
                download.save_as(filename)
                self.data.append({"file": filename, "year": year})
                print(f"[OK] Downloaded: {filename}")
            else:
                print(f"[WARNING] Export button not available for year {year}")
            
            self.page.wait_for_timeout(1000)
    
    def execute(self):
        """Main execution logic for Form 26AS workflow"""
        self.navigate_to_form_26as()
        self.export_pdf()
        print(f"[OK] Form 26AS export completed")
