export interface KpiDefinition {
  id: string
  name: string
  description?: string
  category: 'productivity' | 'financial' | 'client_health' | 'custom'
  unit?: string
  data_source: 'manual' | 'auto'
  computation_config?: Record<string, unknown>
  is_prebuilt: boolean
  is_active: boolean
  sort_order: number
  created_at: string
}

export interface ScorecardTemplate {
  id: string
  name: string
  description?: string
  frequency: string
  is_active: boolean
  kpi_definition_ids?: string[]
  created_at: string
}

export interface Scorecard {
  id: string
  name: string
  period_start: string
  period_end: string
  status: 'draft' | 'in_review' | 'published' | 'archived'
  template_id?: string
  created_by: string
  meeting_date?: string
  meeting_notes?: string
  published_at?: string
  created_at: string
  updated_at: string
}

export interface KpiEntry {
  id: string
  scorecard_id: string
  kpi_definition_id: string
  kpi_name: string
  kpi_category: string
  kpi_unit?: string
  target_value?: number
  actual_value?: number
  previous_value?: number
  status?: 'on_track' | 'at_risk' | 'behind' | 'achieved'
  notes?: string
  sort_order: number
  created_at: string
}

export interface ScorecardDetail extends Scorecard {
  kpi_entries: KpiEntry[]
  attendees: Attendee[]
  action_items: ActionItem[]
  comments: Comment[]
}

export interface Attendee {
  id: string
  user_id: string
  role: string
  created_at: string
}

export interface ActionItem {
  id: string
  kpi_entry_id?: string
  assigned_to: string
  title: string
  description?: string
  due_date?: string
  status: 'open' | 'in_progress' | 'completed'
  created_at: string
}

export interface Comment {
  id: string
  scorecard_id: string
  kpi_entry_id?: string
  user_id: string
  content: string
  created_at: string
}

export interface User {
  id: string
  email: string
  name: string
  role: string
  avatar_url?: string
  org_id: string
  org_name: string
}

export interface Client {
  id: string
  org_id: string
  name: string
  entity_type: string
  status: 'active' | 'inactive' | 'quarterly'
  properties?: Record<string, unknown>
  integration_id?: string
  close_day?: number
  created_at: string
  updated_at: string
}

export interface ClientDashboard {
  client: Client
  task_count: number
  completed_tasks: number
  bank_transaction_count: number
  journal_entry_count: number
}

export interface TaskList {
  id: string
  client_id: string
  name: string
  sort_order: number
  is_template: boolean
  created_at: string
}

export interface Task {
  id: string
  task_list_id: string
  parent_id?: string
  name: string
  description?: string
  assignee_id?: string
  due_date?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'todo' | 'in_progress' | 'review' | 'done'
  tags: string[]
  is_recurring: boolean
  recurring_schedule?: Record<string, unknown>
  sort_order: number
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface TaskDetail extends Task {
  comments: TaskComment[]
  attachments: TaskAttachment[]
  assignee?: User
  sub_tasks?: Task[]
}

export interface TaskComment {
  id: string
  task_id: string
  user_id: string
  content: string
  attachment_url?: string
  created_at: string
}

export interface TaskAttachment {
  id: string
  task_id: string
  user_id: string
  file_name: string
  file_url: string
  file_type: string
  created_at: string
}

export interface BankConnection {
  id: string
  client_id: string
  provider: 'qbo' | 'xero' | 'plaid'
  external_account_id: string
  account_name: string
  account_type: string
  last_synced_at?: string
  is_active: boolean
}

export interface BankTransaction {
  id: string
  bank_connection_id: string
  external_id: string
  date: string
  amount: number
  description: string
  vendor_name?: string
  category?: string
  status: 'pending' | 'matched' | 'classified' | 'needs_review' | 'posted'
  classification_tier: 'match' | 'rule' | 'manual' | 'unclassified'
  matched_transaction_id?: string
  posted_at?: string
  created_at: string
}

export interface ClassificationRule {
  id: string
  client_id: string
  conditions: Record<string, unknown>
  actions: Record<string, unknown>
  priority: number
  is_active: boolean
  created_at: string
}

export interface JournalEntry {
  id: string
  client_id: string
  user_id: string
  description: string
  date: string
  source: 'manual' | 'recurring' | 'accrual'
  status: 'draft' | 'ready' | 'posted' | 'error'
  external_id?: string
  posted_at?: string
  created_at: string
}

export interface JournalEntryDetail extends JournalEntry {
  lines: JournalEntryLine[]
}

export interface JournalEntryLine {
  id: string
  journal_entry_id: string
  account_name: string
  account_external_id: string
  debit_amount: number
  credit_amount: number
  description?: string
  class?: string
  location?: string
}

export interface ReviewReport {
  id: string
  client_id: string
  name: string
  report_type: 'expense_consistency' | 'uncategorized' | 'missing_payees' | 'parent_account_coding' | 'class_inconsistency' | 'missing_attachments' | 'saved_search'
  filters?: Record<string, unknown>
  is_active: boolean
  created_at: string
}

export interface ReviewFinding {
  id: string
  report_id: string
  transaction_external_id: string
  transaction_date: string
  transaction_amount: number
  transaction_description: string
  issue: string
  suggested_action?: string
  status: 'open' | 'resolved' | 'ignored'
  resolved_by?: string
  resolved_at?: string
}

export interface ReportPackage {
  id: string
  client_id: string
  name: string
  period_start: string
  period_end: string
  status: 'draft' | 'published'
  sections?: ReportSection[]
  published_at?: string
  created_at: string
}

export interface ReportSection {
  id: string
  report_package_id: string
  section_type: 'cover_sheet' | 'executive_summary' | 'profit_loss' | 'balance_sheet' | 'cash_flow' | 'kpi_metrics' | 'ap_aging' | 'ar_aging' | 'top_customers' | 'top_vendors' | 'notes'
  config?: Record<string, unknown>
  data?: Record<string, unknown>
  sort_order: number
}

export interface PortalMessage {
  id: string
  client_id: string
  sender_type: 'firm' | 'client'
  sender_id: string
  content: string
  message_type: 'question' | 'answer' | 'document_request' | 'general'
  related_transaction_id?: string
  attachment_url?: string
  is_read: boolean
  created_at: string
}

export interface PortalDocument {
  id: string
  client_id: string
  uploaded_by: 'firm' | 'client'
  user_id: string
  file_url: string
  file_name: string
  doc_type: 'receipt' | 'statement' | 'tax_doc' | 'contract' | 'other'
  created_at: string
}

export interface PortalBranding {
  logo_url?: string
  primary_color?: string
  domain?: string
}

export interface Receipt {
  id: string
  client_id: string
  upload_method: 'portal' | 'email' | 'text' | 'mobile' | 'api'
  file_url: string
  file_name: string
  ocr_text?: string
  extracted_data?: Record<string, unknown>
  status: 'processing' | 'ready' | 'matched' | 'posted'
  matched_transaction_id?: string
  posted_at?: string
  created_at: string
}

export interface AccrualSchedule {
  id: string
  client_id: string
  name: string
  type: 'prepaid_expense' | 'fixed_asset' | 'accrued_expense' | 'deferred_revenue'
  total_amount: number
  start_date: string
  end_date?: string
  recognition_method: 'straight_line' | 'custom'
  journal_entry_template?: Record<string, unknown>
  status: 'active' | 'completed' | 'paused'
  created_at: string
}

export interface AccrualEntry {
  id: string
  schedule_id: string
  period_date: string
  recognized_amount: number
  journal_entry_id?: string
  status: 'pending' | 'posted'
  posted_at?: string
}

export interface AccrualScheduleDetail extends AccrualSchedule {
  entries: AccrualEntry[]
}

export interface TaxReturn {
  id: string
  client_id: string
  tax_year: number
  form_type: string
  status: 'draft' | 'in_progress' | 'review' | 'ready_to_file' | 'filed'
  assigned_to?: string
  due_date?: string
  filed_date?: string
  created_at: string
}

export interface TaxOrganizer {
  id: string
  client_id: string
  tax_year: number
  form_json: Record<string, unknown>
  status: 'draft' | 'published' | 'completed'
  completed_at?: string
  created_at: string
}

export interface SignatureRequest {
  id: string
  tax_return_id: string
  signer_email: string
  signer_name: string
  document_url: string
  auth_method: 'kba' | 'email'
  status: 'pending' | 'sent' | 'signed' | 'expired'
  signed_at?: string
  created_at: string
}

export interface EmailMessage {
  id: string
  org_id: string
  client_id?: string
  from_address: string
  to_address: string[]
  subject: string
  body_text: string
  body_html?: string
  external_id: string
  thread_id: string
  received_at: string
  is_read: boolean
  is_deleted: boolean
}

export interface Integration {
  id: string
  org_id: string
  provider: 'qbo' | 'xero' | 'netsuite' | 'sage'
  access_token?: string
  refresh_token?: string
  token_expires_at?: string
  realm_id?: string
  is_active: boolean
  last_sync_at?: string
  created_at: string
}

export interface SyncLog {
  id: string
  integration_id: string
  entity_type: string
  status: 'running' | 'success' | 'partial' | 'error'
  records_synced: number
  error_message?: string
  started_at: string
  completed_at?: string
}

export interface GstRegistration {
  id: string
  client_id: string
  gstin: string
  trade_name?: string
  legal_name: string
  address?: string
  state_code: string
  state_name: string
  registration_type: string
  taxpayer_type: string
  constitution?: string
  status: string
  registration_date?: string
  cancellation_date?: string
  filing_frequency: string
  is_composition: boolean
  e_invoice_enabled: boolean
  e_waybill_enabled: boolean
  gst_practice_head?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface HsnSacCode {
  id: string
  code: string
  description: string
  type: 'hsn' | 'sac'
  gst_rate: number
  cgst_rate: number
  sgst_rate: number
  igst_rate: number
  cess_rate: number
  compensation_cess: number
  chapter?: string
  is_active: boolean
  effective_from?: string
  effective_to?: string
  created_at: string
  updated_at: string
}

export interface GstInvoiceLine {
  id?: string
  invoice_id?: string
  hsn_sac_code: string
  description: string
  quantity: number
  unit_price: number
  taxable_value: number
  gst_rate: number
  cgst_rate: number
  sgst_rate: number
  igst_rate: number
  cgst_amount: number
  sgst_amount: number
  igst_amount: number
  cess_amount: number
  total_amount: number
  sort_order: number
}

export interface GstInvoice {
  id: string
  client_id: string
  gst_registration_id: string
  invoice_number: string
  invoice_date: string
  invoice_type: string
  supply_type: string
  supply_place: string
  is_inter_state: boolean
  customer_name: string
  customer_gstin?: string
  customer_address?: string
  customer_state_code?: string
  total_taxable_value: number
  total_cgst: number
  total_sgst: number
  total_igst: number
  total_cess: number
  total_invoice_value: number
  e_invoice_irn?: string
  e_waybill_number?: string
  irn_generated_at?: string
  status: 'draft' | 'final' | 'cancelled'
  irn_status: string
  filed_in_gstr: boolean
  gstr_period?: string
  notes?: string
  created_at: string
  updated_at: string
  lines?: GstInvoiceLine[]
}

export interface GstReturn {
  id: string
  client_id: string
  gst_registration_id: string
  return_type: string
  financial_year: string
  return_period: string
  due_date: string
  filing_date?: string
  status: 'pending' | 'in_progress' | 'filed' | 'error'
  total_outward_taxable: number
  total_outward_tax: number
  total_inward_taxable: number
  total_inward_tax: number
  total_liability: number
  total_credit: number
  net_payable: number
  itc_claimed: number
  late_fee: number
  interest: number
  total_paid: number
  arn?: string
  error_message?: string
  return_data?: Record<string, unknown>
  filed_by?: string
  created_at: string
  updated_at: string
}

export interface ChartOfAccount {
  id: string
  org_id: string
  code: string
  name: string
  type: string
  subtype?: string
  schedule?: string
  is_schedule_iii: boolean
  parent_code?: string
  is_active: boolean
  description?: string
  sort_order: number
  created_at: string
  updated_at: string
}

export interface FinancialYear {
  id: string
  org_id: string
  fy: string
  start_date: string
  end_date: string
  is_current: boolean
  is_locked: boolean
  previous_fy?: string
}

export interface Organization {
  id: string
  name: string
  slug: string
  created_at: string
}
