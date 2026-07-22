import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FileSearch, Search, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { ReviewReport, Client } from '@/types'

const reportTypeLabels: Record<string, string> = {
  expense_consistency: 'Expense Consistency',
  uncategorized: 'Uncategorized Transactions',
  missing_payees: 'Missing Payees',
  parent_account_coding: 'Parent Account Coding',
  class_inconsistency: 'Class Inconsistency',
  missing_attachments: 'Missing Attachments',
  saved_search: 'Saved Search',
}

export function FileReviewPage() {
  const [reports, setReports] = useState<ReviewReport[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({
    client_id: '',
    name: '',
    report_type: 'expense_consistency',
    filters: '{}',
  })

  const load = async () => {
    setLoading(true)
    try {
      const [r, c] = await Promise.all([
        apiFetch<ReviewReport[]>('/file-review/reports'),
        apiFetch<Client[]>('/clients/'),
      ])
      setReports(r)
      setClients(c)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    let filters = {}
    try { filters = JSON.parse(form.filters) } catch {}
    await apiFetch('/file-review/reports', {
      method: 'POST',
      body: JSON.stringify({ ...form, filters }),
    })
    setShowModal(false)
    setForm({ client_id: '', name: '', report_type: 'expense_consistency', filters: '{}' })
    load()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">File Review</h1>
          <p className="text-muted-foreground mt-1">Run review reports to find issues in your data.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          New Report
        </Button>
      </div>

      {reports.length === 0 ? (
        <Card className="p-12 text-center">
          <FileSearch className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No review reports</h3>
          <p className="text-muted-foreground mb-4">
            Create a review report to scan for anomalies and issues.
          </p>
          <Button className="gap-2" onClick={() => setShowModal(true)}>
            <Plus className="w-4 h-4" />
            New Report
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {reports.map((r) => (
            <Link key={r.id} to={`/file-review/${r.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold">{r.name}</h3>
                    <Badge variant={r.is_active ? 'success' : 'outline'}>
                      {r.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {reportTypeLabels[r.report_type] || r.report_type}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Review Report</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.client_id}
                    onChange={(e) => setForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Name</label>
                  <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Report Type</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={form.report_type}
                    onChange={(e) => setForm((f) => ({ ...f, report_type: e.target.value }))}
                  >
                    {Object.entries(reportTypeLabels).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Filters (JSON)</label>
                  <textarea
                    className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring min-h-[80px] font-mono"
                    value={form.filters}
                    onChange={(e) => setForm((f) => ({ ...f, filters: e.target.value }))}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
                  <Button type="submit">Create</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
