from .models import RawITR
from datetime import date

class TaxCalendarEngine:
    
    @staticmethod
    def generate_advance_tax_schedule(itr: RawITR) -> list:
        """
        Generates the 4-quarter schedule based on estimated tax liability.
        """
        # Estimate current year liability (Simple projection: Last year + 10%)
        estimated_tax = itr.tax_paid * 1.10 
        
        schedule = [
            {"quarter": "Q1", "due_date": f"2024-06-15", "percent": 0.15},
            {"quarter": "Q2", "due_date": f"2024-09-15", "percent": 0.45},
            {"quarter": "Q3", "due_date": f"2024-12-15", "percent": 0.75},
            {"quarter": "Q4", "due_date": f"2025-03-15", "percent": 1.00},
        ]
        
        results = []
        for item in schedule:
            amount = estimated_tax * item['percent']
            
            # Simple status check
            status = "Upcoming"
            if date.today().strftime("%Y-%m-%d") > item['due_date']:
                status = "Overdue"
            
            results.append({
                "section": "234C",
                "due_date": item['due_date'],
                "amount": round(amount, 2),
                "status": status
            })
            
        return results