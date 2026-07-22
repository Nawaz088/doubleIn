import re
from decimal import Decimal
from typing import Optional

GSTIN_PATTERN = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$")

ALLOWED_GST_RATES = [0, 0.25, 1, 1.5, 3, 5, 6, 12, 18, 28]

STATE_CODES: dict[str, str] = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman & Diu", "26": "Dadra & Nagar Haveli", "27": "Maharashtra",
    "28": "Andhra Pradesh (old)", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu",
    "34": "Puducherry", "35": "Andaman & Nicobar", "36": "Telangana",
    "37": "Andhra Pradesh",
}

RETURN_TYPES: dict[str, str] = {
    "GSTR1": "GSTR-1 (Outward Supplies)",
    "GSTR3B": "GSTR-3B (Monthly Return)",
    "GSTR4": "GSTR-4 (Composition Dealer)",
    "GSTR5": "GSTR-5 (Non-Resident Taxpayer)",
    "GSTR6": "GSTR-6 (Input Service Distributor)",
    "GSTR7": "GSTR-7 (TDS Deductor)",
    "GSTR8": "GSTR-8 (TCS Collector)",
    "GSTR9": "GSTR-9 (Annual Return)",
    "GSTR9C": "GSTR-9C (Audit Report)",
    "GSTR10": "GSTR-10 (Final Return)",
    "CMP08": "CMP-08 (Composition Payment)",
    "ITC04": "ITC-04 (Job Work)",
}


def validate_gstin(gstin: str) -> bool:
    return bool(GSTIN_PATTERN.match(gstin.strip().upper()))


def parse_gstin(gstin: str) -> Optional[dict]:
    gstin = gstin.strip().upper()
    if not validate_gstin(gstin):
        return None
    state_code = gstin[:2]
    pan = gstin[2:12]
    entity_type_code = gstin[12]
    default_z = gstin[13]
    checksum = gstin[14]
    return {
        "state_code": state_code,
        "state_name": STATE_CODES.get(state_code, "Unknown"),
        "pan": pan,
        "entity_type": entity_type_code,
        "checksum": checksum,
    }


def compute_gst_split(
    taxable_value: float,
    gst_rate: float,
    is_inter_state: bool,
    cess_rate: float = 0,
) -> dict:
    if gst_rate not in ALLOWED_GST_RATES:
        raise ValueError(f"GST rate {gst_rate}% is not valid")

    half_rate = gst_rate / 2
    gst_amount = round(taxable_value * gst_rate / 100, 2)
    cess_amount = round(taxable_value * cess_rate / 100, 2)

    if is_inter_state:
        return {
            "cgst_rate": 0,
            "sgst_rate": 0,
            "igst_rate": gst_rate,
            "cgst_amount": 0,
            "sgst_amount": 0,
            "igst_amount": gst_amount,
            "cess_amount": cess_amount,
        }
    else:
        half_gst = round(gst_amount / 2, 2)
        return {
            "cgst_rate": half_rate,
            "sgst_rate": half_rate,
            "igst_rate": 0,
            "cgst_amount": half_gst,
            "sgst_amount": gst_amount - half_gst,
            "igst_amount": 0,
            "cess_amount": cess_amount,
        }


def compute_invoice(
    lines: list[dict],
    is_inter_state: bool,
    seller_state_code: str,
    customer_state_code: Optional[str] = None,
) -> dict:
    computed_lines = []
    total_taxable = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
    total_cess = 0

    for i, line in enumerate(lines):
        qty = float(line.get("quantity", 1))
        unit_price = float(line.get("unit_price", 0))
        gst_rate = float(line.get("gst_rate", 0))
        cess_rate = float(line.get("cess_rate", 0))
        taxable_value = round(qty * unit_price, 2)

        split = compute_gst_split(taxable_value, gst_rate, is_inter_state, cess_rate)

        total = round(taxable_value + split["cgst_amount"] + split["sgst_amount"] + split["igst_amount"] + split["cess_amount"], 2)

        computed_lines.append({
            "hsn_sac_code": line.get("hsn_sac_code", ""),
            "description": line.get("description", ""),
            "quantity": qty,
            "unit_price": unit_price,
            "taxable_value": taxable_value,
            "gst_rate": gst_rate,
            **split,
            "total_amount": total,
            "sort_order": i,
        })
        total_taxable += taxable_value
        total_cgst += split["cgst_amount"]
        total_sgst += split["sgst_amount"]
        total_igst += split["igst_amount"]
        total_cess += split["cess_amount"]

    total_invoice_value = round(total_taxable + total_cgst + total_sgst + total_igst + total_cess, 2)

    return {
        "lines": computed_lines,
        "total_taxable_value": round(total_taxable, 2),
        "total_cgst": round(total_cgst, 2),
        "total_sgst": round(total_sgst, 2),
        "total_igst": round(total_igst, 2),
        "total_cess": round(total_cess, 2),
        "total_invoice_value": total_invoice_value,
    }


def get_due_date(return_type: str, return_period: str) -> Optional[str]:
    period_map = {
        "GSTR1": "11", "GSTR3B": "20", "GSTR4": "18",
        "GSTR5": "13", "GSTR6": "13", "GSTR7": "10",
        "GSTR8": "10", "GSTR9": "31", "GSTR9C": "31",
        "GSTR10": "30", "CMP08": "18", "ITC04": "25",
    }
    day = period_map.get(return_type)
    if not day or len(return_period) != 7:
        return None
    month = return_period[:2]
    year = return_period[3:]
    if return_type in ("GSTR9", "GSTR9C", "GSTR10"):
        return f"{year}-{day}"
    return f"{year}-{month}-{day}"


def get_financial_year(date_str: str) -> str:
    year = int(date_str[:4])
    month = int(date_str[5:7])
    if month >= 4:
        return f"{year}-{year + 1}"
    return f"{year - 1}-{year}"
