from app.core.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_email(self, to: str, subject: str, body: str, html_body: str = None):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def sync_bank_transactions(self, connection_id: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(bind=True, max_retries=3)
def process_ocr(self, receipt_id: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def generate_report_pdf(self, report_id: str):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def generate_accrual_entries():
    pass


@celery_app.task
def send_daily_digest():
    pass


@celery_app.task
def sync_integration(self, integration_id: str):
    pass
