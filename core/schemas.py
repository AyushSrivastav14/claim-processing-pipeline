from pydantic import BaseModel, Field
from typing import List, Literal

# --- 1. ID Agent Schema ---
class IdentityInfo(BaseModel):
    """Extraction schema for identity and policy documents."""
    patient_name: str = Field(description="Full name of the patient")
    dob: str = Field(description="Date of birth")
    id_numbers: List[str] = Field(description="Any government or patient ID numbers found")
    policy_details: str = Field(description="Insurance policy numbers or details")

# --- 2. Discharge Summary Agent Schema ---
class DischargeSummary(BaseModel):
    """Extraction schema for hospital discharge summaries."""
    diagnosis: str = Field(description="Primary diagnosis or reason for admission")
    admission_date: str = Field(description="Date the patient was admitted")
    discharge_date: str = Field(description="Date the patient was discharged")
    physician_details: str = Field(description="Name of the attending physician or doctor")

# --- 3. Itemized Bill Agent Schemas ---
class LineItem(BaseModel):
    """A single billed item or service."""
    description: str = Field(description="Name of the service, charge, or medication")
    cost: float = Field(description="The financial cost of the item")

class ItemizedBill(BaseModel):
    """Extraction schema for financial bills and receipts."""
    line_items: List[LineItem] = Field(description="List of all individual billed items")
    total_amount: float = Field(description="The final total amount claimed or billed")


class PageClassification(BaseModel):
    """Schema for the Segregator Agent to classify a single PDF page."""
    category: Literal[
        "claim_forms", 
        "cheque_or_bank_details", 
        "identity_document", 
        "itemized_bill", 
        "discharge_summary", 
        "prescription", 
        "investigation_report", 
        "cash_receipt", 
        "other"
    ] = Field(description="The exact document category for the provided page text.")