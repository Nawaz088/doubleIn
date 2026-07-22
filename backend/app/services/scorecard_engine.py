import asyncio
import uuid
from datetime import date

from sqlalchemy import text
from app.core.database import async_session

KPI_COMPUTATIONS: dict[str, str] = {
    "tasks-completed": """
        SELECT COUNT(*) FROM tasks t
        JOIN task_lists tl ON t.task_list_id = tl.id
        JOIN clients c ON tl.client_id = c.id
        WHERE c.org_id = :org_id
          AND t.completed_at BETWEEN :pstart AND :pend
    """,
    "closes-on-time-pct": """
        SELECT
          CASE WHEN COUNT(*) = 0 THEN 0
            ELSE COUNT(*) FILTER (WHERE t.completed_at <= t.due_date OR t.due_date IS NULL) * 100.0 / COUNT(*)
          END
        FROM tasks t
        JOIN task_lists tl ON t.task_list_id = tl.id
        JOIN clients c ON tl.client_id = c.id
        WHERE c.org_id = :org_id
          AND t.completed_at BETWEEN :pstart AND :pend
          AND t.status = 'done'
    """,
    "avg-close-time": """
        SELECT AVG(EXTRACT(EPOCH FROM (t.completed_at - t.created_at)) / 86400.0)
        FROM tasks t
        JOIN task_lists tl ON t.task_list_id = tl.id
        JOIN clients c ON tl.client_id = c.id
        WHERE c.org_id = :org_id
          AND t.completed_at BETWEEN :pstart AND :pend
          AND t.status = 'done'
    """,
    "reports-generated": """
        SELECT COUNT(*) FROM report_packages rp
        JOIN clients c ON rp.client_id = c.id
        WHERE c.org_id = :org_id
          AND rp.created_at BETWEEN :pstart AND :pend
    """,
    "utilization-rate": """
        SELECT COUNT(*) FILTER (WHERE role IS NOT NULL)
        FROM users
        WHERE org_id = :org_id AND is_active = true
    """,
    "net-client-growth": """
        SELECT (
          (SELECT COUNT(*) FROM clients WHERE org_id = :org_id AND created_at BETWEEN :pstart AND :pend)
          -
          (SELECT COUNT(*) FROM clients WHERE org_id = :org_id AND status = 'inactive' AND updated_at BETWEEN :pstart AND :pend)
        )
    """,
    "portal-adoption-rate": """
        SELECT CASE
          WHEN (SELECT COUNT(*) FROM clients WHERE org_id = :org_id AND status = 'active') = 0 THEN 0
          ELSE (
            SELECT COUNT(DISTINCT client_id) FROM portal_activities
            WHERE org_id = :org_id AND created_at BETWEEN :pstart AND :pend AND action_type = 'login'
          ) * 100.0 / NULLIF(
            (SELECT COUNT(*) FROM clients WHERE org_id = :org_id AND status = 'active'), 0
          )
        END
    """,
    "open-action-items": """
        SELECT COUNT(*) FROM scorecard_action_items sai
        JOIN scorecards s ON sai.scorecard_id = s.id
        WHERE s.org_id = :org_id
          AND sai.created_at BETWEEN :pstart AND :pend
          AND sai.status != 'completed'
    """,
}


async def compute_kpi(
    kpi_name: str,
    org_id: uuid.UUID,
    period_start: date,
    period_end: date,
) -> str | None:
    sql = KPI_COMPUTATIONS.get(kpi_name)
    if not sql:
        return None

    try:
        async with async_session() as session:
            result = await session.execute(
                text(sql),
                {"org_id": org_id, "pstart": period_start, "pend": period_end},
            )
            val = result.scalar()
            if val is not None:
                return str(round(float(val), 4))
    except Exception:
        pass
    return "0"


async def compute_all_auto_kpis(
    org_id: uuid.UUID,
    period_start: date,
    period_end: date,
):
    results = {}
    tasks = [compute_kpi(name, org_id, period_start, period_end) for name in KPI_COMPUTATIONS]
    names = list(KPI_COMPUTATIONS.keys())
    computed = await asyncio.gather(*tasks)
    for name, value in zip(names, computed):
        results[name] = value if value is not None else "0"
    return results
