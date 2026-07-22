from datetime import date, timedelta
from typing import Optional

INCOME_TAX_SLABS_OLD = [
    {"max": 250000, "rate": 0},
    {"max": 500000, "rate": 5},
    {"max": 1000000, "rate": 20},
    {"max": float("inf"), "rate": 30},
]

INCOME_TAX_SLABS_NEW = [
    {"max": 300000, "rate": 0},
    {"max": 600000, "rate": 5},
    {"max": 900000, "rate": 10},
    {"max": 1200000, "rate": 15},
    {"max": 1500000, "rate": 20},
    {"max": float("inf"), "rate": 30},
]

SENIOR_SAVINGS_EXEMPTION = 50000
STANDARD_DEDUCTION = 50000
SECTION_80C_LIMIT = 150000
SECTION_80D_LIMIT = 25000
SECTION_80D_SENIOR_LIMIT = 50000
SECTION_80G_LIMIT = float("inf")
SECTION_80E_LIMIT = float("inf")
HRA_EXEMPTION_LIMIT = float("inf")

ADVANCE_TAX_DUE_DATES = [
    (1, "06-15", "15-Jun"),
    (2, "09-15", "15-Sep"),
    (3, "12-15", "15-Dec"),
    (4, "03-15", "15-Mar"),
]

ADVANCE_TAX_PERCENTAGES = [15, 45, 75, 100]

ITR_DUE_DATES: dict[str, str] = {
    "ITR1": "07-31",
    "ITR2": "07-31",
    "ITR3": "07-31",
    "ITR4": "07-31",
    "ITR5": "10-31",
    "ITR6": "10-31",
    "ITR7": "10-31",
}

MCA_DUE_DATES: dict[str, str] = {
    "AOC4": "10-30",
    "MGT7": "10-30",
    "MGT7A": "10-30",
    "DIR3KYC": "09-30",
    "INC22": "30 days",
    "PAS3": "30 days",
    "CHG1": "30 days",
}


def get_itr_due_date(form_type: str, financial_year: str) -> str:
    due = ITR_DUE_DATES.get(form_type, "07-31")
    year_end = int(financial_year.split("-")[1])
    return f"{year_end}-{due}"


def get_assessment_year(financial_year: str) -> str:
    parts = financial_year.split("-")
    return f"{int(parts[1])}-{int(parts[1]) + 1}"


def get_advance_tax_schedule(financial_year: str) -> list[dict]:
    fy_start = int(financial_year.split("-")[0])
    schedule = []
    for i, (inst, date_str, label) in enumerate(ADVANCE_TAX_DUE_DATES):
        month = int(date_str.split("-")[0])
        year = fy_start if month >= 4 else fy_start + 1
        schedule.append({
            "installment": inst,
            "due_date": f"{year}-{date_str}",
            "label": label,
            "due_percentage": ADVANCE_TAX_PERCENTAGES[i],
        })
    return schedule


def calculate_income_tax(
    gross_income: float,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    deductions_80g: float = 0,
    deductions_80e: float = 0,
    hra_exemption: float = 0,
    lta_exemption: float = 0,
    other_exemptions: float = 0,
    old_regime: bool = True,
    is_senior: bool = False,
    is_super_senior: bool = False,
    tds_credited: float = 0,
    advance_tax_paid: float = 0,
) -> dict:
    total_exemptions = hra_exemption + lta_exemption + other_exemptions
    gross_total = gross_income - total_exemptions

    if not old_regime:
        standard_deduction = 75000 if False else 0
        total_deductions = 0
    else:
        standard_deduction = STANDARD_DEDUCTION
        capped_80c = min(deductions_80c, SECTION_80C_LIMIT)
        capped_80d = min(deductions_80d, SECTION_80D_SENIOR_LIMIT if is_senior else SECTION_80D_LIMIT)
        total_deductions = capped_80c + capped_80d + deductions_80g + deductions_80e

    taxable_income = max(0, gross_total - standard_deduction - total_deductions)

    slabs = INCOME_TAX_SLABS_OLD if old_regime else INCOME_TAX_SLABS_NEW
    if is_super_senior and old_regime:
        slabs[0]["max"] = 500000

    tax = 0
    remaining = taxable_income
    prev_max = 0
    for slab in slabs:
        if remaining <= 0:
            break
        slab_max = slab["max"]
        slab_income = min(remaining, slab_max - prev_max)
        if slab_income > 0:
            tax += slab_income * slab["rate"] / 100
        remaining -= slab_income
        prev_max = slab_max

    rebate_87a = 0
    if old_regime and taxable_income <= 500000:
        rebate_87a = min(tax, 12500)
    elif not old_regime and taxable_income <= 700000:
        rebate_87a = min(tax, 25000)

    tax_after_rebate = max(0, tax - rebate_87a)

    surcharge_rate = 0
    if taxable_income > 5000000 and taxable_income <= 10000000:
        surcharge_rate = 10
    elif taxable_income > 10000000 and taxable_income <= 20000000:
        surcharge_rate = 15
    elif taxable_income > 20000000 and taxable_income <= 50000000:
        surcharge_rate = 25
    elif taxable_income > 50000000:
        surcharge_rate = 37

    surcharge = round(tax_after_rebate * surcharge_rate / 100, 2)
    education_cess = round((tax_after_rebate + surcharge) * 4 / 100, 2)

    total_tax = round(tax_after_rebate + surcharge + education_cess, 2)
    total_tax_paid = round(tds_credited + advance_tax_paid, 2)
    refund_amount = max(0, round(total_tax_paid - total_tax, 2))
    tax_payable = max(0, round(total_tax - total_tax_paid, 2))

    return {
        "gross_income": round(gross_income, 2),
        "exemptions": round(total_exemptions, 2),
        "gross_total": round(gross_total, 2),
        "standard_deduction": standard_deduction,
        "deductions_80c": round(min(deductions_80c, SECTION_80C_LIMIT), 2),
        "deductions_80d": round(min(deductions_80d, SECTION_80D_SENIOR_LIMIT if is_senior else SECTION_80D_LIMIT), 2),
        "total_deductions": round(total_deductions, 2),
        "taxable_income": round(taxable_income, 2),
        "tax_before_rebate": round(tax, 2),
        "rebate_87a": rebate_87a,
        "tax_after_rebate": tax_after_rebate,
        "surcharge_rate": surcharge_rate,
        "surcharge": surcharge,
        "education_cess": education_cess,
        "total_tax": total_tax,
        "tds_credited": round(tds_credited, 2),
        "advance_tax_paid": round(advance_tax_paid, 2),
        "total_tax_paid": total_tax_paid,
        "refund_amount": refund_amount,
        "tax_payable": tax_payable,
        "regime": "old" if old_regime else "new",
    }
