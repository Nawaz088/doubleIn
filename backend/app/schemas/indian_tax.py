import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator


GSTIN_PATTERN = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$"


class GstRegistrationCreate(BaseModel):
    client_id: uuid.UUID
    gstin: str
    trade_name: Optional[str] = None
    legal_name: str
    address: Optional[str] = None
    state_code: str
    state_name: str
    registration_type: str = "regular"
    taxpayer_type: str = "regular"
    constitution: Optional[str] = None
    registration_date: Optional[date] = None
    filing_frequency: str = "monthly"
    is_composition: bool = False
    e_invoice_enabled: bool = False
    e_waybill_enabled: bool = False
    gst_practice_head: Optional[str] = None

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: str) -> str:
        v = v.upper().strip()
        if not __import__("re").match(GSTIN_PATTERN, v):
            raise ValueError("Invalid GSTIN format")
        return v


class GstRegistrationUpdate(BaseModel):
    trade_name: Optional[str] = None
    legal_name: Optional[str] = None
    address: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    registration_type: Optional[str] = None
    taxpayer_type: Optional[str] = None
    constitution: Optional[str] = None
    status: Optional[str] = None
    registration_date: Optional[date] = None
    cancellation_date: Optional[date] = None
    filing_frequency: Optional[str] = None
    is_composition: Optional[bool] = None
    e_invoice_enabled: Optional[bool] = None
    e_waybill_enabled: Optional[bool] = None
    gst_practice_head: Optional[str] = None
    is_active: Optional[bool] = None


class GstRegistrationResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    gstin: str
    trade_name: Optional[str] = None
    legal_name: str
    address: Optional[str] = None
    state_code: str
    state_name: str
    registration_type: str
    taxpayer_type: str
    constitution: Optional[str] = None
    status: str
    registration_date: Optional[date] = None
    cancellation_date: Optional[date] = None
    filing_frequency: str
    is_composition: bool
    e_invoice_enabled: bool
    e_waybill_enabled: bool
    gst_practice_head: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HsnSacCodeCreate(BaseModel):
    code: str
    description: str
    type: str = "hsn"
    gst_rate: float
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
    igst_rate: Optional[float] = None
    cess_rate: float = 0
    compensation_cess: float = 0
    chapter: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    @field_validator("gst_rate")
    @classmethod
    def validate_gst_rate(cls, v: float) -> float:
        allowed = [0, 0.25, 1, 1.5, 3, 5, 6, 12, 18, 28]
        if v not in allowed:
            raise ValueError(f"GST rate must be one of {allowed}")
        return v


class HsnSacCodeUpdate(BaseModel):
    description: Optional[str] = None
    gst_rate: Optional[float] = None
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
    igst_rate: Optional[float] = None
    cess_rate: Optional[float] = None
    compensation_cess: Optional[float] = None
    chapter: Optional[str] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class HsnSacCodeResponse(BaseModel):
    id: uuid.UUID
    code: str
    description: str
    type: str
    gst_rate: float
    cgst_rate: float
    sgst_rate: float
    igst_rate: float
    cess_rate: float
    compensation_cess: float
    chapter: Optional[str] = None
    is_active: bool
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GstInvoiceLineCreate(BaseModel):
    hsn_sac_code: str
    description: str
    quantity: float
    unit_price: float
    gst_rate: float
    is_inter_state: bool = False
    cess_rate: float = 0
    sort_order: int = 0


class GstInvoiceLineResponse(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    hsn_sac_code: str
    description: str
    quantity: float
    unit_price: float
    taxable_value: float
    gst_rate: float
    cgst_rate: float
    sgst_rate: float
    igst_rate: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    cess_amount: float
    total_amount: float
    sort_order: int

    model_config = {"from_attributes": True}


class GstInvoiceCreate(BaseModel):
    client_id: uuid.UUID
    gst_registration_id: uuid.UUID
    invoice_number: str
    invoice_date: date
    invoice_type: str = "regular"
    supply_type: str = "goods"
    supply_place: str
    is_inter_state: bool = False
    customer_name: str
    customer_gstin: Optional[str] = None
    customer_address: Optional[str] = None
    customer_state_code: Optional[str] = None
    notes: Optional[str] = None
    lines: list[GstInvoiceLineCreate]


class GstInvoiceUpdate(BaseModel):
    status: Optional[str] = None
    e_invoice_irn: Optional[str] = None
    e_waybill_number: Optional[str] = None
    irn_status: Optional[str] = None
    filed_in_gstr: Optional[bool] = None
    gstr_period: Optional[str] = None
    notes: Optional[str] = None


class GstInvoiceResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    gst_registration_id: uuid.UUID
    invoice_number: str
    invoice_date: date
    invoice_type: str
    supply_type: str
    supply_place: str
    is_inter_state: bool
    customer_name: str
    customer_gstin: Optional[str] = None
    customer_address: Optional[str] = None
    customer_state_code: Optional[str] = None
    total_taxable_value: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    total_cess: float
    total_invoice_value: float
    e_invoice_irn: Optional[str] = None
    e_waybill_number: Optional[str] = None
    irn_generated_at: Optional[datetime] = None
    status: str
    irn_status: str
    filed_in_gstr: bool
    gstr_period: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GstInvoiceDetailResponse(GstInvoiceResponse):
    lines: list[GstInvoiceLineResponse] = []


class GstReturnCreate(BaseModel):
    client_id: uuid.UUID
    gst_registration_id: uuid.UUID
    return_type: str
    financial_year: str
    return_period: str
    due_date: date


class GstReturnUpdate(BaseModel):
    status: Optional[str] = None
    filing_date: Optional[date] = None
    total_outward_taxable: Optional[float] = None
    total_outward_tax: Optional[float] = None
    total_inward_taxable: Optional[float] = None
    total_inward_tax: Optional[float] = None
    total_liability: Optional[float] = None
    total_credit: Optional[float] = None
    net_payable: Optional[float] = None
    itc_claimed: Optional[float] = None
    late_fee: Optional[float] = None
    interest: Optional[float] = None
    total_paid: Optional[float] = None
    arn: Optional[str] = None
    error_message: Optional[str] = None
    return_data: Optional[dict] = None


class GstReturnResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    gst_registration_id: uuid.UUID
    return_type: str
    financial_year: str
    return_period: str
    due_date: date
    filing_date: Optional[date] = None
    status: str
    total_outward_taxable: float
    total_outward_tax: float
    total_inward_taxable: float
    total_inward_tax: float
    total_liability: float
    total_credit: float
    net_payable: float
    itc_claimed: float
    late_fee: float
    interest: float
    total_paid: float
    arn: Optional[str] = None
    error_message: Optional[str] = None
    return_data: Optional[dict] = None
    filed_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GstComputeRequest(BaseModel):
    lines: list[GstInvoiceLineCreate]
    is_inter_state: bool = False
    customer_state_code: Optional[str] = None
    seller_state_code: str


class GstComputeResponse(BaseModel):
    lines: list[GstInvoiceLineResponse]
    total_taxable_value: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    total_cess: float
    total_invoice_value: float
