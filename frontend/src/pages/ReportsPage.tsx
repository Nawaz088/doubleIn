import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, BarChart3, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { ReportPackage, Client } from '@/types'

const statusConfig: Record<string, { label: string; variant: 'success' | 'outline' }> = {
  draft: { label: 'Draft', variant: 'outline' },
  published: { label: 'Published', variant: 'success' },
}

export function ReportsPage() {
  const [reports, setReports] = useState<ReportPackage[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({
    client_id: '',
    name: '',
    period_start: '',
    period_end: '',
  })

  const load = async () => {
    setLoading(true)
    try {
      const [r, c] = await Promise.all([
        apiFetch<ReportPackage[]>('/reports/'),
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
    await apiFetch('/reports/', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    setShowModal(false)
    setForm({ client_id: '', name: '', period_start: '', period_end: '' })
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
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground mt-1">Generate and publish report packages.</p>
        </div>
        <Button size="sm" className="gap-2" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" />
          New Report
        </Button>
      </div>

      {reports.length === 0 ? (
        <Card className="p-12 text-center">
          <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No reports yet</h3>
          <p className="text-muted-foreground mb-4">
            Generate your first report package for client reporting.
          </p>
          <Button className="gap-2" onClick={() => setShowModal(true)}>
            <Plus className="w-4 h-4" />
            New Report
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {reports.map((r) => (
            <Link key={r.id} to={`/reports/${r.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
                <CardContent className="p-6 space-y-3">
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-lg">{r.name}</h3>
                    <Badge variant={statusConfig[r.status]?.variant || 'outline'}>
                      {statusConfig[r.status]?.label || r.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5" />
                    {r.period_start} ― {r.period_end}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Report Package</CardTitle></CardHeader>
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
                  <label className="text-sm font-medium block mb-1">Period Start</label>
                  <Input type="date" value={form.period_start} onChange={(e) => setForm((f) => ({ ...f, period_start: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Period End</label>
                  <Input type="date" value={form.period_end} onChange={(e) => setForm((f) => ({ ...f, period_end: e.target.value }))} required />
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
