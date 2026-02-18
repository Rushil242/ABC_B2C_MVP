
from sqlalchemy.orm import Session
from .. import models, rule_engine
import json
import logging
import os

def process_ais_data(db: Session, pan: str, ais_data: dict):
    """
    Processes AIS JSON data and populates AIS_Entry and TDS_Entry tables.
    """
    try:
        logging.info(f"Processing AIS Data for {pan}")
        
        # 1. Clear existing AIS entries for this PAN (or maybe strictly by FY if available)
        # ForMVP, let's clear all to avoid duplicates on re-sync
        db.query(models.AIS_Entry).filter(models.AIS_Entry.user_pan == pan).delete()
        db.query(models.TDS_Entry).filter(models.TDS_Entry.user_pan == pan).delete()
        
        count_ais = 0
        count_tds = 0

        # Disclaimer: The structure of AIS JSON varies. We will try to find lists of data.
        # Often it comes as { "AIS": { "TaxpayerInfo": ..., "TDS": [ ... ] } }
        
        # Helper to recursively find lists of dicts that look like transactions
        def extract_transactions(data, parent_key=""):
            transactions = []
            if isinstance(data, dict):
                for k, v in data.items():
                    transactions.extend(extract_transactions(v, k))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        # Heuristic to identify if this dict is a transaction
                        # It should have some amount and description fields
                        if any(key.lower() in ['amount', 'count', 'date'] for key in item.keys()):
                             # Add context from parent key
                             item['_parent_category'] = parent_key
                             transactions.append(item)
            return transactions

        all_transactions = extract_transactions(ais_data)
        
        for item in all_transactions:
            # Map to AIS_Entry
            # We look for common keys
            amount = item.get("amount", item.get("Amount", item.get("gross_amount", 0)))
            description = item.get("description", item.get("Description", item.get("Narration", "")))
            category = item.get("information_category", item.get("InformationCategory", item.get("_parent_category", "Unknown")))
            source = item.get("source", item.get("Source", "AIS"))
            fy = item.get("financial_year", item.get("FY", "Unknown"))
            
            # TDS Specific Checks
            if "TDS" in category.upper() or "TCS" in category.upper():
                # Map to TDS_Entry
                tds_entry = models.TDS_Entry(
                    user_pan=pan,
                    type="TDS" if "TDS" in category.upper() else "TCS",
                    section=item.get("section", item.get("Section", "Unknown")),
                    date=item.get("date", item.get("Date", "Unknown")),
                    tds_amount=str(amount), # Storing gross amount as TDS amount for now or look for specific tax field
                    total_amount=str(item.get("total_amount", item.get("TotalAmount", amount)))
                )
                # Refine TDS Amount if available
                if "tax_deposited" in item:
                     tds_entry.tds_amount = str(item["tax_deposited"])
                elif "TDS_Deposited" in item:
                     tds_entry.tds_amount = str(item["TDS_Deposited"])
                
                db.add(tds_entry)
                count_tds += 1

            # Always add to AIS_Entry for comprehensive view
            try:
                amt_float = float(str(amount).replace(",", ""))
            except:
                amt_float = 0.0

            ais_entry = models.AIS_Entry(
                user_pan=pan,
                fy=fy,
                category=category,
                description=description,
                amount=amt_float,
                source=source
            )
            db.add(ais_entry)
            count_ais += 1

        db.commit()
        logging.info(f"Ingested {count_ais} AIS entries and {count_tds} TDS entries.")
        return True, f"Synced {count_ais} records."

    except Exception as e:
        logging.error(f"Error processing AIS: {e}")
        db.rollback()
        return False, str(e)

def process_26as_file(db: Session, pan: str, file_path: str):
    """
    Logs the download of 26AS file.
    """
    logging.info(f"26AS File Downloaded for {pan}: {file_path}")
    # In future: Parse PDF/HTML
    return True, "File downloaded."

def process_eproceedings_file(db: Session, pan: str, file_path: str):
    """
    Logs the download of E-Proceedings file.
    """
    logging.info(f"E-Proceedings File Downloaded for {pan}: {file_path}")
    # In future: Parse Excel
    return True, "File downloaded."
