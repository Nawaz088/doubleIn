# DoubleHQ Clone — Complete Build Guide

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vite + React 19 + TypeScript + Tailwind CSS v4 + Radix UI |
| **Backend** | Python 3.12+ / FastAPI + SQLAlchemy 2.0 + Alembic |
| **Database** | PostgreSQL 16 |
| **Cache/Queue** | Redis + Celery |
| **Auth** | JWT (access + refresh) + magic link support |
| **File Storage** | S3-compatible (MinIO for dev, AWS S3 for prod) |
| **OCR** | Tesseract (self-hosted, free) |
| **Real-time** | WebSocket via FastAPI + Socket.IO |
| **Email** | SendGrid / Resend |
| **Infra** | Docker Compose + Nginx (single Hetzner VPS) |
| **Design** | shadcn/ui component library + Framer Motion |

## Cost Pillars

**Infrastructure**: Single Hetzner VPS (€9-42/mo) runs everything — app, DB, Redis, Celery, MinIO, Nginx. No managed services until 100+ clients.

**Variable costs**: ~$0 per client (no AI APIs). Tesseract OCR is free. All compute happens on our own server.

**Margins**: 97%+ from day one.

---

## Directory Structure

```
doublehq-clone/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── clients.py
│   │   │       │   ├── tasks.py
│   │   │       │   ├── bank_feeds.py
│   │   │       │   ├── transactions.py
│   │   │       │   ├── file_review.py
│   │   │       │   ├── reports.py
│   │   │       │   ├── receipts.py
│   │   │       │   ├── accruals.py
│   │   │       │   ├── portal.py
│   │   │       │   ├── inbox.py
│   │   │       │   ├── tax.py
│   │   │       │   ├── integrations.py
│   │   │       │   └── webhooks.py
│   │   │       └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── client.py
│   │   │   ├── task.py
│   │   │   ├── bank_transaction.py
│   │   │   ├── journal_entry.py
│   │   │   ├── report.py
│   │   │   ├── receipt.py
│   │   │   ├── accrual.py
│   │   │   ├── portal_message.py
│   │   │   ├── email.py
│   │   │   ├── tax_return.py
│   │   │   ├── integration.py
│   │   │   └── audit_log.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── client.py
│   │   │   ├── task.py
│   │   │   ├── bank_feed.py
│   │   │   ├── transaction.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── integrations/
│   │   │   │   ├── qbo.py
│   │   │   │   ├── xero.py
│   │   │   │   ├── netsuite.py
│   │   │   │   ├── sage.py
│   │   │   │   └── zapier.py
│   │   │   ├── ocrengine.py
│   │   │   └── email_service.py
│   │   ├── tasks/  (Celery)
│   │   │   ├── bank_sync.py
│   │   │   ├── email_sync.py
│   │   │   └── report_generation.py
│   │   └── utils/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── alembic.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          (shadcn components)
│   │   │   ├── layout/
│   │   │   ├── dashboard/
│   │   │   ├── clients/
│   │   │   ├── tasks/
│   │   │   ├── bank-feeds/
│   │   │   ├── file-review/
│   │   │   ├── reports/
│   │   │   ├── receipts/
│   │   │   ├── accruals/
│   │   │   ├── portal/
│   │   │   ├── inbox/
│   │   │   ├── tax/
│   │   │   ├── integrations/
│   │   │   └── settings/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile
│
└── docs/
```

---

## Data Model (Core Tables)

### Users & Organizations (Multi-tenant)

```sql
Organization
  id: UUID PK
  name: str
  slug: str (unique)
  created_at: datetime

User
  id: UUID PK
  org_id: FK -> Organization
  email: str unique
  password_hash: str
  name: str
  role: enum(admin, manager, member, client)
  avatar_url: str?
  created_at: datetime

OrgMembership
  id: UUID PK
  user_id: FK -> User
  org_id: FK -> Organization
  role: enum(owner, admin, member)
  invited_by: FK -> User?
```

### Clients (the entities being managed)

```sql
Client
  id: UUID PK
  org_id: FK -> Organization
  name: str
  entity_type: enum(llc, corp, sole_prop)
  status: enum(active, inactive, quarterly)
  properties: JSONB (custom fields, key-value)
  integration_id: FK -> Integration?
  close_day: int
  created_at: datetime
  updated_at: datetime
```

### Task Management (Close Page)

```sql
TaskList
  id: UUID PK
  client_id: FK -> Client
  name: str (e.g. "Month-End Close", "Payroll", "Tax")
  sort_order: int
  is_template: bool
  created_at: datetime

Task
  id: UUID PK
  task_list_id: FK -> TaskList
  parent_id: FK -> Task?
  name: str
  description: text?
  assignee_id: FK -> User?
  due_date: date?
  priority: enum(low, medium, high, critical)
  status: enum(todo, in_progress, review, done)
  tags: str[]
  is_recurring: bool
  recurring_schedule: JSONB?
  sort_order: int
  completed_at: datetime?
  created_at: datetime
  updated_at: datetime

TaskComment
  id: UUID PK
  task_id: FK -> Task
  user_id: FK -> User
  content: text
  attachment_url: str?
  created_at: datetime

TaskAttachment
  id: UUID PK
  task_id: FK -> Task
  user_id: FK -> User
  file_name: str
  file_url: str
  file_type: str
  created_at: datetime
```

### Bank Feed / Transactions

```sql
BankConnection
  id: UUID PK
  client_id: FK -> Client
  provider: enum(qbo, xero, plaid)
  external_account_id: str
  account_name: str
  account_type: str
  last_synced_at: datetime?
  is_active: bool

BankTransaction
  id: UUID PK
  bank_connection_id: FK -> BankConnection
  external_id: str
  date: date
  amount: decimal
  description: str
  vendor_name: str?
  category: str?
  status: enum(pending, matched, classified, needs_review, posted)
  classification_tier: enum(match, rule, manual, unclassified)
  matched_transaction_id: FK -> Transaction?
  posted_at: datetime?
  created_at: datetime

ClassificationRule
  id: UUID PK
  client_id: FK -> Client
  conditions: JSONB
  actions: JSONB
  priority: int
  is_active: bool
  created_at: datetime
```

### Journal Entries

```sql
JournalEntry
  id: UUID PK
  client_id: FK -> Client
  user_id: FK -> User
  description: text
  date: date
  source: enum(manual, recurring, accrual)
  status: enum(draft, ready, posted, error)
  external_id: str?
  posted_at: datetime?
  created_at: datetime

JournalEntryLine
  id: UUID PK
  journal_entry_id: FK -> JournalEntry
  account_name: str
  account_external_id: str
  debit_amount: decimal
  credit_amount: decimal
  description: str?
  class: str?
  location: str?
```

### File Review

```sql
ReviewReport
  id: UUID PK
  client_id: FK -> Client
  name: str
  report_type: enum(
    expense_consistency,
    uncategorized,
    missing_payees,
    parent_account_coding,
    class_inconsistency,
    missing_attachments,
    saved_search
  )
  filters: JSONB
  is_active: bool
  created_at: datetime

ReviewFinding
  id: UUID PK
  report_id: FK -> ReviewReport
  transaction_external_id: str
  transaction_date: date
  transaction_amount: decimal
  transaction_description: str
  issue: text
  suggested_action: text?
  status: enum(open, resolved, ignored)
  resolved_by: FK -> User?
  resolved_at: datetime?
```

### Reporting

```sql
ReportPackage
  id: UUID PK
  client_id: FK -> Client
  name: str
  period_start: date
  period_end: date
  status: enum(draft, published)
  sections: JSONB
  published_at: datetime?
  created_at: datetime

ReportSection
  id: UUID PK
  report_package_id: FK -> ReportPackage
  section_type: enum(
    cover_sheet,
    executive_summary,
    profit_loss,
    balance_sheet,
    cash_flow,
    kpi_metrics,
    ap_aging,
    ar_aging,
    top_customers,
    top_vendors,
    notes
  )
  config: JSONB
  data: JSONB?
  sort_order: int
```

### Receipts

```sql
Receipt
  id: UUID PK
  client_id: FK -> Client
  upload_method: enum(portal, email, text, mobile, api)
  file_url: str
  file_name: str
  ocr_text: text?
  extracted_data: JSONB?
  status: enum(processing, ready, matched, posted)
  matched_transaction_id: FK -> Transaction?
  posted_at: datetime?
  created_at: datetime
```

### Accruals

```sql
AccrualSchedule
  id: UUID PK
  client_id: FK -> Client
  name: str
  type: enum(prepaid_expense, fixed_asset, accrued_expense, deferred_revenue)
  total_amount: decimal
  start_date: date
  end_date: date?
  recognition_method: enum(straight_line, custom)
  journal_entry_template: JSONB
  status: enum(active, completed, paused)
  created_at: datetime

AccrualEntry
  id: UUID PK
  schedule_id: FK -> AccrualSchedule
  period_date: date
  recognized_amount: decimal
  journal_entry_id: FK -> JournalEntry?
  status: enum(pending, posted)
  posted_at: datetime?
```

### Client Portal

```sql
PortalMessage
  id: UUID PK
  client_id: FK -> Client
  sender_type: enum(firm, client)
  sender_id: FK -> User
  content: text
  message_type: enum(question, answer, document_request, general)
  related_transaction_id: str?
  attachment_url: str?
  is_read: bool
  created_at: datetime

PortalDocument
  id: UUID PK
  client_id: FK -> Client
  uploaded_by: enum(firm, client)
  user_id: FK -> User
  file_url: str
  file_name: str
  doc_type: enum(receipt, statement, tax_doc, contract, other)
  created_at: datetime
```

### Inbox (Email)

```sql
EmailMessage
  id: UUID PK
  org_id: FK -> Organization
  client_id: FK -> Client?
  from_address: str
  to_address: str[]
  subject: str
  body_text: text
  body_html: text?
  external_id: str
  thread_id: str
  received_at: datetime
  is_read: bool
  is_deleted: bool

EmailTaskLink
  id: UUID PK
  email_id: FK -> EmailMessage
  task_id: FK -> Task
  created_at: datetime
```

### Tax Suite

```sql
TaxReturn
  id: UUID PK
  client_id: FK -> Client
  tax_year: int
  form_type: str
  status: enum(draft, in_progress, review, ready_to_file, filed)
  assigned_to: FK -> User?
  due_date: date
  filed_date: date?
  created_at: datetime

SignatureRequest
  id: UUID PK
  tax_return_id: FK -> TaxReturn
  signer_email: str
  signer_name: str
  document_url: str
  auth_method: enum(kba, email)
  status: enum(pending, sent, signed, expired)
  signed_at: datetime?
  created_at: datetime

TaxOrganizer
  id: UUID PK
  client_id: FK -> Client
  tax_year: int
  form_json: JSONB
  status: enum(draft, published, completed)
  completed_at: datetime?
  created_at: datetime
```

### Integrations

```sql
Integration
  id: UUID PK
  org_id: FK -> Organization
  provider: enum(qbo, xero, netsuite, sage)
  access_token: str (encrypted)
  refresh_token: str (encrypted)
  token_expires_at: datetime
  realm_id: str?
  is_active: bool
  last_sync_at: datetime?
  created_at: datetime

SyncLog
  id: UUID PK
  integration_id: FK -> Integration
  entity_type: str
  status: enum(running, success, partial, error)
  records_synced: int
  error_message: text?
  started_at: datetime
  completed_at: datetime?
```

---

## API Route Design (FastAPI)

```
/api/v1/
├── auth/
│   ├── POST /login               Email + password
│   ├── POST /register            Create account + org
│   ├── POST /magic-link          Send magic link email
│   ├── POST /magic-link/verify   Verify magic link token
│   ├── POST /refresh             Refresh access token
│   ├── POST /logout              Revoke tokens
│   └── GET /me                   Current user + org
│
├── org/
│   ├── GET /settings             Org settings
│   ├── PUT /settings             Update org
│   ├── GET /members              List org members
│   ├── POST /members/invite      Invite user
│   ├── PUT /members/{id}         Update role
│   └── DELETE /members/{id}      Remove member
│
├── clients/
│   ├── GET /                     List clients (paginated, filterable)
│   ├── POST /                    Create client
│   ├── GET /{id}                 Client details
│   ├── PUT /{id}                 Update client
│   ├── DELETE /{id}              Deactivate
│   ├── GET /{id}/properties      Custom property schema
│   ├── PUT /{id}/properties      Update properties
│   └── GET /{id}/dashboard       Dashboard summary data
│
├── tasks/
│   ├── GET /                     List tasks (filterable)
│   ├── POST /                    Create task
│   ├── GET /{id}                 Task detail with comments
│   ├── PUT /{id}                 Update task
│   ├── DELETE /{id}              Delete task
│   ├── POST /{id}/comments       Add comment
│   ├── POST /{id}/attachments    Upload attachment
│   ├── POST /{id}/assign         Assign user
│   └── GET /templates            List task templates
│
├── task-lists/
│   ├── GET /                     List task lists for client
│   ├── POST /                    Create task list
│   ├── PUT /{id}                 Update (name, sort)
│   ├── DELETE /{id}              Delete with cascade
│   └── PUT /{id}/reorder         Reorder tasks
│
├── bank-feeds/
│   ├── GET /connections          List bank connections
│   ├── POST /connections         Connect bank account
│   ├── POST /connections/sync    Trigger sync
│   ├── GET /transactions         List with filters
│   ├── POST /transactions/{id}/approve
│   ├── POST /transactions/{id}/classify
│   ├── POST /transactions/bulk-approve
│   ├── GET /rules                List classification rules
│   ├── POST /rules               Create rule
│   ├── PUT /rules/{id}           Update rule
│   └── DELETE /rules/{id}        Delete rule
│
├── transactions/
│   ├── GET /journal-entries      List JEs
│   ├── POST /journal-entries     Create JE
│   ├── PUT /journal-entries/{id} Update JE
│   ├── POST /journal-entries/{id}/post  Post to QBO/Xero
│   └── GET /journal-entries/{id}
│
├── file-review/
│   ├── GET /reports              List review reports
│   ├── POST /reports             Create report
│   ├── GET /reports/{id}         Findings
│   ├── POST /reports/{id}/findings/{fkid}/resolve
│   └── POST /reports/{id}/refresh  Re-run report
│
├── reports/
│   ├── POST /generate            Generate report package
│   ├── GET /                     List report packages
│   ├── GET /{id}                 Report detail with sections
│   ├── PUT /{id}                 Update customization
│   ├── POST /{id}/publish        Publish to portal
│   └── GET /{id}/export/pdf      Export to PDF
│
├── receipts/
│   ├── GET /                     List receipts
│   ├── POST /upload              Upload receipt (multipart)
│   ├── GET /{id}                 Receipt detail
│   ├── PUT /{id}                 Update coding
│   ├── POST /{id}/post           Post to ledger
│   └── POST /{id}/reprocess      Re-run OCR
│
├── accruals/
│   ├── GET /schedules            List schedules
│   ├── POST /schedules           Create schedule
│   ├── GET /schedules/{id}       Detail with entries
│   ├── PUT /schedules/{id}       Update schedule
│   ├── POST /schedules/{id}/entries/generate
│   ├── POST /entries/{id}/post
│   └── GET /                     All entries with filters
│
├── portal/
│   ├── GET /messages             List messages for client
│   ├── POST /messages            Send message
│   ├── PUT /messages/{id}/read   Mark read
│   ├── GET /documents            List documents
│   ├── POST /documents/upload    Upload doc
│   ├── GET /branding             Get portal branding
│   ├── PUT /branding             Update branding
│   └── GET /activity             Client activity feed
│
├── inbox/
│   ├── GET /                     List emails (paginated)
│   ├── GET /{id}                 Email detail
│   ├── POST /{id}/convert-task   Convert to task
│   ├── POST /{id}/comment        Add internal comment
│   ├── PUT /{id}/read            Mark read
│   └── GET /{id}/context         Client context sidebar
│
├── tax/
│   ├── GET /returns              List tax returns
│   ├── POST /returns             Create return
│   ├── PUT /returns/{id}         Update status, assignee
│   ├── GET /organizers           List organizers
│   ├── POST /organizers          Create/publish organizer
│   ├── POST /organizers/{id}/submit  Client submits
│   ├── POST /signatures          Send signature request
│   ├── POST /signatures/{id}/resend
│   └── GET /filings              Filing history
│
├── integrations/
│   ├── GET /                     List integrations
│   ├── POST /qbo/auth            Initiate QBO OAuth
│   ├── POST /qbo/callback        QBO OAuth callback
│   ├── POST /xero/auth           Initiate Xero OAuth
│   ├── POST /xero/callback       Xero OAuth callback
│   ├── POST /{id}/sync           Trigger full sync
│   ├── POST /{id}/disconnect     Remove integration
│   └── GET /{id}/sync-logs       Sync history
│
├── users/
│   ├── GET /                     List org users
│   ├── GET /me                   Current user profile
│   ├── PUT /me                   Update profile
│   ├── GET /me/preferences       User preferences
│   └── PUT /me/preferences       Update preferences
│
└── webhooks/
    ├── POST /qbo                 QBO webhook receiver
    ├── POST /xero                Xero webhook receiver
    └── POST /sendgrid            Inbound email webhook
```

---

## Frontend Component Tree

```
App
├── AuthLayout
│   ├── LoginPage
│   ├── RegisterPage
│   └── MagicLinkPage
│
├── AppLayout (authenticated)
│   ├── Sidebar
│   │   ├── OrgSwitcher
│   │   ├── NavItem (Dashboard, Clients, Tasks, Bank Feeds, File Review,
│   │   │           Reports, Receipts, Accruals, Portal, Inbox, Tax,
│   │   │           Integrations, Settings)
│   │   └── UserMenu
│   │
│   ├── TopBar
│   │   ├── SearchCommand (⌘K)
│   │   ├── NotificationsBell
│   │   └── QuickActions
│   │
│   ├── DashboardPage
│   │   ├── KPI cards
│   │   ├── CloseProgressChart
│   │   ├── RecentActivityFeed
│   │   ├── UpcomingDeadlines
│   │   └── TeamWorkload
│   │
│   ├── ClientsPage
│   │   ├── ClientTable (sortable, filterable, custom columns)
│   │   ├── ClientKanbanView
│   │   ├── ClientDetailPage
│   │   │   ├── ClientHeader (name, status, integration, close day)
│   │   │   ├── ClientTabs (Dashboard, Tasks, Bank, Review, Reports,
│   │   │   │               Receipts, Portal, Tax)
│   │   │   └── ClientDashboard
│   │   └── ClientFormModal
│   │
│   ├── TasksPage
│   │   ├── TaskListView
│   │   ├── TaskKanbanView
│   │   ├── TaskDetailPanel
│   │   │   ├── TaskInfo
│   │   │   ├── Description
│   │   │   ├── SubTaskList
│   │   │   ├── CommentThread
│   │   │   ├── Attachments
│   │   │   └── ActivityLog
│   │   └── CreateTaskModal
│   │
│   ├── ClosePage (per client)
│   │   ├── CloseProgressBar
│   │   ├── SectionList (draggable, collapsible)
│   │   │   └── TaskCard (status, assignee, due date)
│   │   └── AddSectionButton
│   │
│   ├── BankFeedsPage
│   │   ├── AccountSelector
│   │   ├── TransactionTable (filterable by tier, status)
│   │   ├── RuleManager
│   │   │   ├── RuleList
│   │   │   └── RuleBuilder
│   │   └── BulkActionBar
│   │
│   ├── JournalEntriesPage
│   │   ├── EntryList
│   │   ├── EntryForm (line item table, editable)
│   │   └── PostToLedgerButton
│   │
│   ├── FileReviewPage
│   │   ├── ReportList
│   │   ├── ReportDetail
│   │   │   ├── FindingTable
│   │   │   └── QuickFixPanel
│   │   └── SavedSearchBuilder
│   │
│   ├── ReportsPage
│   │   ├── ReportList
│   │   ├── ReportBuilder
│   │   │   ├── SectionSelector
│   │   │   ├── Customizer
│   │   │   └── PreviewPane
│   │   └── PublishedReports
│   │
│   ├── ReceiptsPage
│   │   ├── UploadZone (drag & drop)
│   │   ├── ReceiptList / Grid
│   │   ├── ReceiptDetail
│   │   │   ├── ImageViewer
│   │   │   ├── OCRDataDisplay
│   │   │   └── CodingForm
│   │   └── PostToLedgerButton
│   │
│   ├── AccrualsPage
│   │   ├── ScheduleList
│   │   ├── ScheduleDetail
│   │   │   ├── ScheduleInfo
│   │   │   ├── EntryTimeline
│   │   │   └── EntryTable
│   │   └── CreateScheduleWizard
│   │
│   ├── PortalPage
│   │   ├── BrandingEditor
│   │   │   ├── LogoUpload
│   │   │   ├── ColorPicker
│   │   │   ├── DomainConfig
│   │   │   └── LivePreview
│   │   ├── MessageThreadView
│   │   └── DocumentLibrary
│   │
│   ├── InboxPage
│   │   ├── EmailList (gmail-like)
│   │   ├── EmailDetail
│   │   │   ├── EmailBody
│   │   │   ├── ConvertToTaskButton
│   │   │   ├── InternalComments
│   │   │   └── ClientContextSidebar
│   │   └── UnifiedInbox
│   │
│   ├── TaxPage
│   │   ├── TaxReturnList
│   │   ├── TaxReturnDetail
│   │   │   ├── StatusTracker
│   │   │   ├── OrganizerFormPreview
│   │   │   ├── SignatureRequests
│   │   │   └── DocumentStorage
│   │   ├── OrganizerBuilder
│   │   └── FilingDashboard
│   │
│   ├── IntegrationsPage
│   │   ├── IntegrationCard (QBO, Xero, NetSuite, Sage)
│   │   ├── ConnectionFlow (OAuth modal)
│   │   ├── SyncStatusIndicator
│   │   └── ZapierTriggerList
│   │
│   └── SettingsPage
│       ├── OrganizationSettings
│       ├── Billing
│       ├── TeamManagement
│       └── NotificationPreferences
│
└── ClientPortalLayout (separate sub-path)
    ├── DashboardView
    ├── QuestionsView
    ├── DocumentUpload
    ├── ReportsView
    └── TaxStatusView
```

---

## Implementation Plan (16 Weeks — Full Product, No AI)

### Week 1 — Foundation
- [ ] Docker Compose (PostgreSQL, Redis, MinIO, backend, frontend)
- [ ] FastAPI project with config, database, CORS, error handling
- [ ] SQLAlchemy models: Organization, User, OrgMembership
- [ ] Auth: JWT access + refresh tokens, password hashing
- [ ] Auth endpoints: login, register, refresh, logout, me
- [ ] Vite + React + TypeScript scaffold
- [ ] shadcn/ui setup with theme provider
- [ ] Auth pages: Login, Register, MagicLink
- [ ] AppLayout with sidebar navigation
- [ ] User menu + org switcher

### Week 2 — CRM & Dashboard
- [ ] Client model + CRUD API (full pagination, filtering)
- [ ] Custom client properties (JSONB, dynamic field rendering)
- [ ] Client list page (table view + kanban view toggle)
- [ ] Client detail page with tabs
- [ ] Client form modal (create/edit)
- [ ] Dashboard page with KPI cards
- [ ] CloseProgressChart, RecentActivityFeed, UpcomingDeadlines
- [ ] Dashboard API aggregation endpoint

### Weeks 3-4 — Task Management & Close Page
- [ ] TaskList + Task models + CRUD API
- [ ] Close Page UI (section list, task cards, drag reorder)
- [ ] Task card: status indicator, assignee avatar, due date, priority
- [ ] Task detail slideover (info, description, sub-tasks)
- [ ] Sub-task CRUD
- [ ] Comment thread (real-time via WebSocket)
- [ ] File attachments per task
- [ ] Task templates (create from template, save as template)
- [ ] Activity log per task
- [ ] Recurring tasks (Celery scheduler)
- [ ] Daily digest email (Celery)

### Weeks 5-7 — Integrations (QBO + Xero)
- [ ] Integration model + OAuth state management
- [ ] QBO OAuth 2.0 flow (auth URL, callback, token storage)
- [ ] QBO API client: chart of accounts, transactions, vendors, customers
- [ ] 2-way sync engine (inbound: pull from QBO, outbound: push to QBO)
- [ ] Xero OAuth 1.0a / 2.0 flow
- [ ] Xero API client
- [ ] Webhook receivers (QBO + Xero)
- [ ] SyncLog model + error handling
- [ ] Retry logic for failed syncs
- [ ] Integration management UI (connect, disconnect, sync status)
- [ ] Sync history view

### Week 8 — Bank Feeds (Manual/Rule-Based)
- [ ] BankConnection model + CRUD API
- [ ] BankTransaction model + API
- [ ] Transaction listing with filters (tier, status, date range)
- [ ] Manual classification / approval workflow
- [ ] ClassificationRule CRUD + rule engine
- [ ] Rule builder UI (condition builder)
- [ ] Bulk approve/classify actions
- [ ] Match transactions to open invoices/JEs

### Week 9 — Journal Entries
- [ ] JournalEntry + JournalEntryLine models
- [ ] JE CRUD API
- [ ] JE list page with filters
- [ ] JE form (editable line item table, add/remove rows)
- [ ] JE posting to QBO/Xero
- [ ] JE status tracking (draft → ready → posted)

### Week 10 — File Review
- [ ] ReviewReport + ReviewFinding models + CRUD API
- [ ] Report engine: expense consistency detection
- [ ] Uncategorized transaction finder
- [ ] Missing payees report
- [ ] Parent account coding detection
- [ ] Class/location inconsistency
- [ ] Missing attachments report
- [ ] Saved search (custom filter-based reports)
- [ ] File review UI: report list, finding table, quick fix panel
- [ ] One-click fixes (edit category, add payee, etc.)

### Week 11 — Reports
- [ ] ReportPackage + ReportSection models + CRUD API
- [ ] Report builder UI (drag-drop sections, reorder)
- [ ] Section selector (cover sheet, P&L, balance sheet, cash flow, etc.)
- [ ] Executive summary section
- [ ] KPI metrics with custom formulas
- [ ] Report customization (date range, footnotes, disclaimers)
- [ ] PDF export (WeasyPrint)
- [ ] Report preview pane
- [ ] Publish to client portal

### Week 12 — Client Portal
- [ ] PortalMessage model + API
- [ ] Magic link portal access (separate sub-path or subdomain)
- [ ] Portal branding editor (logo, colors, domain)
- [ ] Message thread view (questions ↔ answers)
- [ ] Document upload for clients
- [ ] Transaction questions flow (ask from bank feed → client responds)
- [ ] Automated reminder emails (Celery)
- [ ] Portal dashboard (open items, reports, tax status)
- [ ] Notification system (in-app + email)

### Week 13 — Receipts
- [ ] Receipt model + upload API
- [ ] Tesseract OCR pipeline (Celery task)
- [ ] Multi-channel upload: portal, email forwarding, drag-drop
- [ ] Receipt list + grid view
- [ ] Receipt detail with image viewer
- [ ] OCR data display + editing
- [ ] Coding form (vendor, category, account mapping)
- [ ] Receipt → transaction matching
- [ ] Post to ledger

### Week 14 — Accruals + 1099s
- [ ] AccrualSchedule + AccrualEntry models
- [ ] Schedule CRUD API
- [ ] Amortization calculation engine (straight-line, custom)
- [ ] Accrual list + detail UI
- [ ] Entry generation (Celery, scheduled)
- [ ] Entry timeline visualization
- [ ] Post entries to QBO/Xero
- [ ] 1099 vendor identification (entity type + YTD spend)
- [ ] W-9 collection (portal request + vendor email)
- [ ] 1099 CSV export by type (NEC, MISC, INT, DIV)

### Week 15 — Tax Suite
- [ ] TaxReturn model + CRUD API
- [ ] Tax task management (assignee, due dates, status)
- [ ] Tax organizer builder (form builder UI)
- [ ] Organizer publishing to client portal
- [ ] KBA e-signature integration (IRS-compliant)
- [ ] Signature request sending + tracking
- [ ] Live tax status tracker (for client portal)
- [ ] Tax document storage (by year)
- [ ] Filing history

### Week 16 — Email Inbox + Polish
- [ ] EmailMessage model + API
- [ ] Gmail API integration (OAuth, sync threads)
- [ ] Outlook API integration
- [ ] Email list UI (gmail-style)
- [ ] Email detail view (body, attachments, thread)
- [ ] Convert email to task (one-click)
- [ ] Internal comments on emails
- [ ] Client context sidebar (linked emails)
- [ ] Unified team inbox
- [ ] Final integration testing
- [ ] Staging deployment + smoke tests
- [ ] Onboarding flow + documentation

---

## Key UI / UX Principles

1. **Dark mode first** — Both themes, optimized for dark
2. **Command palette** — ⌘K for everything
3. **Drag & drop** — Tasks, sections, report builder, kanban
4. **Infinite scroll** — Virtual list for thousands of transactions
5. **Optimistic updates** — UI before API response
6. **Real-time** — WebSocket for comments, task updates, messages
7. **Split-pane layouts** — Detail panels as slideovers
8. **Bulk actions** — Select multiple, act at once
9. **Progress disclosure** — Show advanced features only when needed
10. **Micro-animations** — Framer Motion for transitions
11. **Mobile-responsive** — Works on tablet/phone before native app

---

## Infrastructure (Single VPS, 0-100 Clients)

```
┌─────────────────────────────────────────┐
│         Hetzner CX42 (€18.99/mo)         │
│  8 vCPU, 16GB RAM, 320GB NVMe SSD       │
│                                         │
│  ┌──────────┐  ┌──────────┐             │
│  │ FastAPI   │  │ Nginx    │             │
│  │ (uvicorn) │  │ (reverse │             │
│  │ 4 workers │  │  proxy)  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ PostgreSQL│  │ Redis    │             │
│  │ (15GB)   │  │ (1GB)    │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ Celery   │  │ MinIO    │             │
│  │ (worker) │  │ (files)  │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────────────────────────────┐    │
│  │ React SPA (built static files)   │    │
│  │ served by Nginx                   │    │
│  └──────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## Getting Started

```bash
git clone <repo> && cd doublehq-clone

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
pnpm install
pnpm run dev

# Infrastructure
docker compose up -d postgres redis minio
```

---

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/doublehq
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

QBO_CLIENT_ID=your-qbo-client-id
QBO_CLIENT_SECRET=your-qbo-client-secret
XERO_CLIENT_ID=your-xero-client-id
XERO_CLIENT_SECRET=your-xero-client-secret

SENDGRID_API_KEY=your-sendgrid-key
MAGIC_LINK_BASE_URL=http://localhost:5173

S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=doublehq-files
```
