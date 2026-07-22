from datetime import date
from typing import Optional

TDS_RATES: dict[str, dict] = {
    "194A": {"rate": 10, "threshold": 50000, "threshold_senior": 100000, "name": "Interest on Securities"},
    "194B": {"rate": 30, "threshold": 10000, "name": "Lotteries/Puzzles"},
    "194C": {"rate": 1, "rate_huf": 2, "threshold_single": 30000, "threshold_aggregate": 100000, "name": "Contractor Payments"},
    "194D": {"rate": 10, "threshold": 20000, "name": "Insurance Commission"},
    "194EE": {"rate": 10, "threshold": 2500, "name": "NSS Deposits"},
    "194F": {"rate": 20, "name": "Repurchase by MF/UTI"},
    "194G": {"rate": 5, "threshold": 15000, "name": "Lottery Ticket Commission"},
    "194H": {"rate": 5, "threshold": 15000, "name": "Commission/Brokerage"},
    "194I": {"rate": 10, "rate_plant": 2, "threshold": 240000, "name": "Rent"},
    "194IA": {"rate": 1, "threshold": 5000000, "name": "Property Transfer"},
    "194IB": {"rate": 5, "threshold": 50000, "name": "Rent by Individual/HUF"},
    "194IC": {"rate": 10, "name": "Specified Agreement"},
    "194J": {"rate": 10, "rate_technical": 2, "threshold": 30000, "name": "Professional/Technical Fees"},
    "194K": {"rate": 10, "threshold": 5000, "name": "Income from Units"},
    "194LA": {"rate": 10, "threshold": 250000, "name": "Acquired Property Compensation"},
    "194LB": {"rate": 5, "name": "Infrastructure Debt Fund Interest"},
    "194LC": {"rate": 5, "rate_foreign_loan": 10, "name": "Foreign Loan Interest"},
    "194LD": {"rate": 5, "name": "Bond Interest"},
    "194M": {"rate": 5, "threshold": 5000000, "name": "Certain Payments by Individuals/HUF"},
    "194N": {"rate": 2, "rate_no_itr": 5, "threshold": 1000000, "name": "Cash Withdrawal"},
    "194O": {"rate": 1, "threshold": 500000, "name": "E-Commerce Participants"},
    "194Q": {"rate": 0.1, "threshold": 5000000, "name": "Purchase of Goods"},
    "194R": {"rate": 10, "threshold": 20000, "name": "Benefits/Perquisites"},
    "194S": {"rate": 1, "rate_no_pan": 20, "threshold": 50000, "name": "Virtual Digital Assets"},
    "206C": {"rate": 1, "name": "TCS - Sale of Goods"},
    "206CA": {"rate": 5, "name": "TCS - Specified Goods"},
    "206CB": {"rate": 0.1, "threshold": 5000000, "name": "TCS - Purchase of Goods"},
}

QUARTER_MAP = {
    1: "Q1", 2: "Q1", 3: "Q1",
    4: "Q2", 5: "Q2", 6: "Q2",
    7: "Q3", 8: "Q3", 9: "Q3",
    10: "Q4", 11: "Q4", 12: "Q4",
}

FORM_26Q_DUE = {"Q1": "07-31", "Q2": "10-31", "Q3": "01-31", "Q4": "05-31"}
FORM_24Q_DUE = {"Q1": "07-31", "Q2": "10-31", "Q3": "01-31", "Q4": "05-31"}
FORM_27Q_DUE = {"Q1": "07-31", "Q2": "10-31", "Q3": "01-31", "Q4": "05-31"}
FORM_26QB_DUE = "30 days from end of month"


def get_quarter(month: int) -> str:
    return QUARTER_MAP.get(month, "Q1")


def get_quarter_from_date(d: date) -> str:
    return get_quarter(d.month)


def get_tds_rate(section: str) -> Optional[dict]:
    return TDS_RATES.get(section)


def calculate_tds(
    section: str,
    payment_amount: float,
    is_company: bool = True,
    is_huf: bool = False,
    has_pan: bool = True,
) -> dict:
    rate_info = TDS_RATES.get(section)
    if not rate_info:
        return {"error": f"Unknown TDS section: {section}"}

    rate = rate_info["rate"]
    if section == "194C" and not is_company:
        rate = rate_info.get("rate_huf", rate)
    if section == "194I" and "rate_plant" in rate_info:
        rate = rate_info["rate_plant"]
    if section == "194J" and not is_company and "rate_technical" in rate_info:
        rate = rate_info["rate_technical"]
    if section == "194N" and not has_pan:
        rate = rate_info.get("rate_no_itr", rate)
    if section == "194S" and not has_pan:
        rate = rate_info.get("rate_no_pan", rate)

    tds_amount = round(payment_amount * rate / 100, 2)
    surcharge = 0
    education_cess = round(tds_amount * 4 / 100, 2)
    total_tds = round(tds_amount + surcharge + education_cess, 2)

    return {
        "section": section,
        "rate": rate,
        "payment_amount": payment_amount,
        "tds_amount": tds_amount,
        "surcharge": surcharge,
        "education_cess": education_cess,
        "total_tds": total_tds,
    }


def get_due_date(form_type: str, quarter: str, financial_year: str) -> str:
    due_map = {
        "24Q": FORM_24Q_DUE,
        "26Q": FORM_26Q_DUE,
        "27Q": FORM_27Q_DUE,
    }
    date_str = due_map.get(form_type, {}).get(quarter)
    if not date_str:
        return "Unknown"
    if quarter == "Q4":
        year_end = int(financial_year.split("-")[1])
        return f"{year_end}-{date_str}"
    year_start = int(financial_year.split("-")[0])
    month = int(date_str.split("-")[0])
    if month < 4:
        return f"{year_start + 1}-{date_str}"
    return f"{year_start}-{date_str}"
