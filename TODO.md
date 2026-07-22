# DoubleHQ Clone — Build TODO

## Priority 1: Fix Existing Broken Features

- [x] Fix ReportsPage create form (calls `/reports/generate` instead of `/reports/`)
- [x] Fix BankFeedsPage approve/classify buttons (calls `/approve`, `/classify` instead of PUT `/transactions/{id}`)
- [ ] Fix BankFeedsPage connection UI (no connect form)
- [x] Fix Task creation UI (no create form on TasksPage)
- [x] Fix Client dashboard (hardcoded zeros for bank/journal counts)
- [ ] Fix Scorecard edit page (reuse create form, no edit logic)
- [x] Fix SettingsPage (calls `/org/settings` which doesn't exist)
- [x] Add missing org/settings GET/PUT endpoints
- [x] Add missing org/members endpoints (list, invite, update, delete)
- [x] Add user profile/preferences endpoints

## Priority 2: Core Infrastructure

- [ ] Alembic migration files (currently using create_all)
- [x] Celery worker configuration
- [x] WebSocket server (for real-time comments, task updates)
- [x] S3/MinIO file upload service (multipart upload)
- [x] Email service (SendGrid/Resend integration)
- [x] Rate limiting middleware
- [x] Audit logging middleware
- [x] Nginx reverse proxy config
- [x] Production deployment config
- [ ] CI/CD pipeline
- [x] DB backup scripts
- [ ] Monitoring setup (self-hosted)

## Priority 3: Authentication & Security

- [x] Magic link login (endpoint + page)
- [x] Password reset / forgot password
- [ ] Email verification
- [ ] 2FA/MFA
- [ ] SSO/SAML
- [ ] Session management (token revocation)
- [x] Token encryption for integrations
- [ ] Token auto-refresh logic
- [ ] IP allowlisting

## Priority 4: Integrations (QBO/Xero)

- [x] QBO OAuth 2.0 flow (auth URL, callback, token storage)
- [x] QBO API client (chart of accounts, transactions, vendors, customers)
- [x] 2-way sync engine (inbound: pull from QBO, outbound: push to QBO)
- [x] Xero OAuth 2.0 flow
- [x] Xero API client
- [x] Webhook receivers (QBO + Xero + SendGrid)
- [ ] Sync error handling + retry logic
- [ ] NetSuite integration
- [ ] Sage integration
- [ ] Zapier integration
- [ ] Plaid bank connection
- [x] Token encryption (AES-256)
- [ ] Token auto-refresh logic
- [x] Sync logs with detailed error reporting

## Priority 5: Bank Feeds

- [ ] Plaid/QBO/Xero actual bank connection
- [ ] Transaction matching to existing JEs
- [x] Rule engine execution (auto-classification)
- [ ] 4-tier classification logic (match/rule/manual/unclassified)
- [ ] Bank reconciliation
- [ ] Transaction matching suggestions
- [ ] Vendor detection
- [ ] Rule builder UI (visual condition builder)

## Priority 6: Journal Entries

- [ ] Balance validation (debit=credit check)
- [ ] Chart of accounts integration
- [x] QBO/Xero posting (actual API call)
- [ ] Recurring JEs
- [ ] JE from accruals (linked)
- [ ] JE from receipts
- [ ] JE templates
- [ ] Edit line items on existing entries

## Priority 7: File Review

- [ ] Expense consistency detection engine
- [ ] Uncategorized transaction finder
- [ ] Missing payees report
- [ ] Parent account coding detection
- [ ] Class inconsistency detection
- [ ] Missing attachments report
- [ ] Saved search builder
- [ ] One-click fixes
- [ ] Finding ignore action

## Priority 8: Reports

- [x] PDF export (WeasyPrint)
- [ ] Report generation engine (populate data from accounting systems)
- [ ] Section data fetching
- [ ] AP/AR aging sections
- [ ] Top customers/vendors sections
- [ ] Report scheduling
- [ ] Report versioning
- [ ] Custom formulas for KPI metrics

## Priority 9: Client Portal

- [ ] Separate client portal layout (subdomain or sub-path)
- [ ] Magic link portal access
- [ ] Custom domain support
- [ ] Branding persisted to DB
- [x] Actual file upload for documents
- [ ] Transaction questions flow
- [ ] Automated reminder emails
- [ ] Client dashboard view
- [ ] Tax status view for clients
- [ ] Report viewing for clients
- [ ] Client-side file upload

## Priority 10: Receipts

- [x] Tesseract OCR pipeline (Celery task)
- [ ] Multi-channel upload (email forwarding, text, mobile)
- [x] Actual file upload (multipart)
- [ ] Receipt-to-transaction matching
- [x] OCR reprocessing
- [ ] Vendor auto-detection
- [ ] Category auto-suggestion

## Priority 11: Accruals

- [ ] Custom recognition method
- [ ] Auto-scheduled entry generation (Celery)
- [ ] JE creation from entries (linked)
- [ ] 1099 vendor identification
- [ ] W-9 collection
- [ ] 1099 CSV export
- [ ] Entry timeline visualization (chart)

## Priority 12: Tax Suite

- [ ] Tax return GET detail endpoint
- [ ] Organizer GET detail endpoint
- [ ] Signature request GET/list endpoints
- [ ] Filing history endpoint
- [ ] KBA e-signature integration (IRS-compliant)
- [ ] Organizer builder UI
- [ ] Organizer publishing to portal
- [ ] Tax document storage
- [ ] Auto-due-date calculation

## Priority 13: Email Inbox

- [ ] Gmail API integration (OAuth, sync threads)
- [ ] Outlook API integration
- [ ] Email sync engine
- [ ] Thread grouping logic
- [ ] Internal comments on emails
- [ ] Client context sidebar
- [ ] Reply/send email
- [ ] Inbound email webhook (SendGrid)
- [ ] Email attachments

## Priority 14: Task Management Enhancements

- [ ] Real-time WebSocket for comments
- [ ] Drag-and-drop reorder UI
- [ ] Recurring task scheduler (Celery)
- [ ] Task templates creation UI
- [ ] Task creation UI (form)
- [ ] Assignee dropdown
- [ ] Actual file upload for attachments
- [ ] Kanban view for tasks
- [ ] Automated task generation
- [ ] Task dependencies
- [ ] Close checklist automation

## Priority 15: Client Management Enhancements

- [ ] Client properties schema validation
- [ ] Kanban view for clients
- [ ] Custom column configuration
- [ ] Client import/export
- [ ] Client dashboard with real bank/journal counts

## Priority 16: Platform Features

- [ ] Global search (⌘K command palette)
- [x] Dark/Light mode toggle
- [ ] Activity feed
- [ ] In-app notifications
- [ ] Email notifications
- [ ] @mentions in comments
- [ ] Mobile-responsive improvements
- [ ] Native mobile app (React Native)
- [ ] API access for partners
- [ ] Usage analytics dashboard

## Priority 17: AI Features (Phase 2)

- [ ] Ask Double (AI chat assistant)
- [ ] AI Transactions (PDF → journal entries)
- [ ] AI Fix This Rec (auto-reconciliation)
- [ ] AI Flux Analysis (variance explanation)
- [ ] AI Journal Entries (auto-suggest)
- [ ] AI Bank Classification (4-tier)
- [ ] AI Financial Summaries
- [ ] Abacor integration (meeting notes → tasks)
- [ ] PDF statement processing
- [ ] Payroll report → JE conversion
- [ ] Loan statement → JE conversion
- [ ] POS export → JE conversion

---

## Progress

| Priority | Status | Notes |
|----------|--------|-------|
| P1: Fix Broken | Not Started | |
| P2: Infrastructure | Not Started | |
| P3: Auth & Security | Not Started | |
| P4: Integrations | Not Started | |
| P5: Bank Feeds | Not Started | |
| P6: Journal Entries | Not Started | |
| P7: File Review | Not Started | |
| P8: Reports | Not Started | |
| P9: Client Portal | Not Started | |
| P10: Receipts | Not Started | |
| P11: Accruals | Not Started | |
| P12: Tax Suite | Not Started | |
| P13: Email Inbox | Not Started | |
| P14: Task Enhancements | Not Started | |
| P15: Client Enhancements | Not Started | |
| P16: Platform Features | Not Started | |
| P17: AI Features | Not Started | |
