from datetime import date, datetime
from typing import Optional


INDIAN_ENTITY_TYPES = [
    ("private_limited", "Private Limited Company"),
    ("public_limited", "Public Limited Company"),
    ("limited_liability_partnership", "Limited Liability Partnership (LLP)"),
    ("partnership_firm", "Partnership Firm"),
    ("sole_proprietorship", "Sole Proprietorship"),
    ("one_person_company", "One Person Company (OPC)"),
    ("section_8_company", "Section 8 Company"),
    ("producer_company", "Producer Company"),
    ("hindu_undivided_family", "Hindu Undivided Family (HUF)"),
    ("association_of_persons", "Association of Persons (AOP)"),
    ("body_of_individuals", "Body of Individuals (BOI)"),
    ("trust", "Trust"),
    ("cooperative_society", "Cooperative Society"),
    ("government_body", "Government Body"),
    ("foreign_company", "Foreign Company"),
]

INR_FORMAT_SPEC = "₹{:,.2f}"


def format_inr(amount: float) -> str:
    return INR_FORMAT_SPEC.format(amount)


def format_inr_indian(amount: float) -> str:
    amount_str = f"{amount:.2f}"
    parts = amount_str.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"

    if len(integer_part) <= 3:
        return f"₹{integer_part}.{decimal_part}"

    last_three = integer_part[-3:]
    rest = integer_part[:-3]

    groups = []
    while rest:
        groups.append(rest[-2:])
        rest = rest[:-2]

    groups.reverse()
    groups.append(last_three)

    return f"₹{','.join(groups)}.{decimal_part}"


def get_indian_financial_year(d: Optional[date] = None) -> str:
    if d is None:
        d = date.today()
    year = d.year
    month = d.month
    if month >= 4:
        return f"{year}-{year + 1}"
    return f"{year - 1}-{year}"


def get_fy_start_end(fy: str) -> tuple[date, date]:
    parts = fy.split("-")
    start_year = int(parts[0])
    end_year = int(parts[1])
    return date(start_year, 4, 1), date(end_year, 3, 31)


def fy_from_date(d: date) -> str:
    return get_indian_financial_year(d)


def get_current_fy() -> str:
    return get_indian_financial_year()


def is_within_fy(d: date, fy: str) -> bool:
    start, end = get_fy_start_end(fy)
    return start <= d <= end


SCHEDULE_III_ACCOUNTS = {
    "equity": {
        "code": "1",
        "name": "EQUITY AND LIABILITIES",
        "children": {
            "shareholders_funds": {
                "code": "1.1",
                "name": "Shareholders' Funds",
                "children": {
                    "share_capital": {"code": "1.1.1", "name": "Share Capital"},
                    "reserves_surplus": {"code": "1.1.2", "name": "Reserves and Surplus"},
                    "money_received_shares": {"code": "1.1.3", "name": "Money Received Against Share Warrants"},
                }
            },
            "non_current_liabilities": {
                "code": "1.2",
                "name": "Non-Current Liabilities",
                "children": {
                    "long_term_borrowings": {"code": "1.2.1", "name": "Long-Term Borrowings"},
                    "deferred_tax": {"code": "1.2.2", "name": "Deferred Tax Liabilities (Net)"},
                    "other_long_term": {"code": "1.2.3", "name": "Other Long-Term Liabilities"},
                    "long_term_provisions": {"code": "1.2.4", "name": "Long-Term Provisions"},
                }
            },
            "current_liabilities": {
                "code": "1.3",
                "name": "Current Liabilities",
                "children": {
                    "short_term_borrowings": {"code": "1.3.1", "name": "Short-Term Borrowings"},
                    "trade_payables": {"code": "1.3.2", "name": "Trade Payables"},
                    "other_current": {"code": "1.3.3", "name": "Other Current Liabilities"},
                    "short_term_provisions": {"code": "1.3.4", "name": "Short-Term Provisions"},
                }
            },
        }
    },
    "assets": {
        "code": "2",
        "name": "ASSETS",
        "children": {
            "non_current_assets": {
                "code": "2.1",
                "name": "Non-Current Assets",
                "children": {
                    "fixed_assets": {"code": "2.1.1", "name": "Fixed Assets"},
                    "goodwill": {"code": "2.1.2", "name": "Goodwill"},
                    "other_intangible": {"code": "2.1.3", "name": "Other Intangible Assets"},
                    "intangible_under_dev": {"code": "2.1.4", "name": "Intangible Assets Under Development"},
                    "non_current_investments": {"code": "2.1.5", "name": "Non-Current Investments"},
                    "deferred_tax_assets": {"code": "2.1.6", "name": "Deferred Tax Assets (Net)"},
                    "long_term_loans": {"code": "2.1.7", "name": "Long-Term Loans and Advances"},
                    "other_non_current": {"code": "2.1.8", "name": "Other Non-Current Assets"},
                }
            },
            "current_assets": {
                "code": "2.2",
                "name": "Current Assets",
                "children": {
                    "inventories": {"code": "2.2.1", "name": "Inventories"},
                    "trade_receivables": {"code": "2.2.2", "name": "Trade Receivables"},
                    "cash_bank": {"code": "2.2.3", "name": "Cash and Cash Equivalents"},
                    "short_term_loans": {"code": "2.2.4", "name": "Short-Term Loans and Advances"},
                    "other_current_assets": {"code": "2.2.5", "name": "Other Current Assets"},
                }
            },
        }
    },
    "income": {
        "code": "3",
        "name": "INCOME",
        "children": {
            "revenue_operations": {"code": "3.1", "name": "Revenue from Operations"},
            "other_income": {"code": "3.2", "name": "Other Income"},
        }
    },
    "expenses": {
        "code": "4",
        "name": "EXPENSES",
        "children": {
            "cost_materials": {"code": "4.1", "name": "Cost of Materials Consumed"},
            "purchases_stock": {"code": "4.2", "name": "Purchases of Stock-in-Trade"},
            "employee_benefits": {"code": "4.3", "name": "Employee Benefits Expense"},
            "finance_costs": {"code": "4.4", "name": "Finance Costs"},
            "depreciation": {"code": "4.5", "name": "Depreciation and Amortization"},
            "other_expenses": {"code": "4.6", "name": "Other Expenses"},
        }
    },
}


def flatten_schedule_iii() -> list[dict]:
    accounts = []
    for section, data in SCHEDULE_III_ACCOUNTS.items():
        for sub_key, sub_data in data.get("children", {}).items():
            if "children" in sub_data:
                for leaf_key, leaf in sub_data["children"].items():
                    accounts.append({
                        "code": leaf["code"],
                        "name": leaf["name"],
                        "type": section,
                        "subtype": sub_data["name"],
                        "schedule": "III",
                        "is_schedule_iii": True,
                    })
            else:
                accounts.append({
                    "code": sub_data["code"],
                    "name": sub_data["name"],
                    "type": section,
                    "subtype": "",
                    "schedule": "III",
                    "is_schedule_iii": True,
                })
    return accounts
