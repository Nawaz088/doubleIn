import { useState, useEffect } from 'react'
import { Plus, FileText, Calendar, ClipboardList, FileCheck, User } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { TaxReturn, TaxOrganizer, Client } from '@/types'

const returnStatusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' | 'danger' }> = {
  draft: { label: 'Draft', variant: 'outline' },
  in_progress: { label: 'In Progress', variant: 'warning' },
  review: { label: 'Review', variant: 'danger' },
  ready_to_file: { label: 'Ready To File', variant: 'success' },
  filed: { label: 'Filed', variant: 'success' },
}

const organizerStatusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' }> = {
  draft: { label: 'Draft', variant: 'outline' },
  published: { label: 'Published', variant: 'success' },
  completed: { label: 'Completed', variant: 'success' },
}

export function TaxPage() {
  const [returns, setReturns] = useState<TaxReturn[]>([])
  const [organizers, setOrganizers] = useState<TaxOrganizer[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'returns' | 'organizers' | 'filings'>('returns')
  const [showReturnModal, setShowReturnModal] = useState(false)
  const [showOrganizerModal, setShowOrganizerModal] = useState(false)

  const [returnForm, setReturnForm] = useState({
    client_id: '',
    tax_year: new Date().getFullYear(),
    form_type: '1040',
    due_date: '',
  })

  const [organizerForm, setOrganizerForm] = useState({
    client_id: '',
    tax_year: new Date().getFullYear(),
  })

  const load = async () => {
    setLoading(true)
    try {
      const [r, o, c] = await Promise.all([
        apiFetch<TaxReturn[]>('/tax/returns'),
        apiFetch<TaxOrganizer[]>('/tax/organizers'),
        apiFetch<Client[]>('/clients/'),
      ])
      setReturns(r)
      setOrganizers(o)
      setClients(c)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreateReturn = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/tax/returns', {
      method: 'POST',
      body: JSON.stringify(returnForm),
    })
    setShowReturnModal(false)
    setReturnForm({ client_id: '', tax_year: new Date().getFullYear(), form_type: '1040', due_date: '' })
    load()
  }

  const handleCreateOrganizer = async (e: React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/tax/organizers', {
      method: 'POST',
      body: JSON.stringify(organizerForm),
    })
    setShowOrganizerModal(false)
    setOrganizerForm({ client_id: '', tax_year: new Date().getFullYear() })
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
          <h1 className="text-3xl font-bold tracking-tight">Tax</h1>
          <p className="text-muted-foreground mt-1">Manage tax returns, organizers, and filings.</p>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        {(['returns', 'organizers', 'filings'] as const).map((tab) => {
          const icons: Record<string, React.ElementType> = {
            returns: FileText,
            organizers: ClipboardList,
            filings: FileCheck,
          }
          const Icon = icons[tab]
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          )
        })}
      </div>

      {activeTab === 'returns' && (
        <>
          <div className="flex justify-end">
            <Button size="sm" className="gap-2" onClick={() => setShowReturnModal(true)}>
              <Plus className="w-4 h-4" />
              New Return
            </Button>
          </div>
          {returns.length === 0 ? (
            <Card className="p-12 text-center">
              <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No tax returns</h3>
              <p className="text-muted-foreground">Create tax returns to track filing progress.</p>
            </Card>
          ) : (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3 text-sm font-medium text-muted-foreground">Year</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Form</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Due Date</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Assignee</th>
                    </tr>
                  </thead>
                  <tbody>
                    {returns.map((r) => (
                      <tr key={r.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                        <td className="p-3 text-sm">{r.tax_year}</td>
                        <td className="p-3 text-sm">{r.form_type}</td>
                        <td className="p-3">
                          <Badge variant={returnStatusConfig[r.status]?.variant || 'outline'}>
                            {returnStatusConfig[r.status]?.label || r.status}
                          </Badge>
                        </td>
                        <td className="p-3 text-sm">
                          {r.due_date ? new Date(r.due_date).toLocaleDateString() : '—'}
                        </td>
                        <td className="p-3 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            {r.assigned_to || 'Unassigned'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}

      {activeTab === 'organizers' && (
        <>
          <div className="flex justify-end">
            <Button size="sm" className="gap-2" onClick={() => setShowOrganizerModal(true)}>
              <Plus className="w-4 h-4" />
              New Organizer
            </Button>
          </div>
          {organizers.length === 0 ? (
            <Card className="p-12 text-center">
              <ClipboardList className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No tax organizers</h3>
              <p className="text-muted-foreground">Create tax organizers for clients to fill out.</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {organizers.map((o) => (
                <Card key={o.id}>
                  <CardContent className="flex items-center justify-between py-4">
                    <div className="flex items-center gap-4">
                      <ClipboardList className="w-6 h-6 text-primary" />
                      <div>
                        <h3 className="font-medium">Tax Year {o.tax_year}</h3>
                      </div>
                    </div>
                    <Badge variant={organizerStatusConfig[o.status]?.variant || 'outline'}>
                      {organizerStatusConfig[o.status]?.label || o.status}
                    </Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === 'filings' && (
        <Card className="p-12 text-center">
          <FileCheck className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">Filing History</h3>
          <p className="text-muted-foreground">Filing history will appear here once returns are filed.</p>
        </Card>
      )}

      {showReturnModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Tax Return</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreateReturn} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={returnForm.client_id}
                    onChange={(e) => setReturnForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Tax Year</label>
                  <Input type="number" value={returnForm.tax_year} onChange={(e) => setReturnForm((f) => ({ ...f, tax_year: parseInt(e.target.value) || 0 }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Form Type</label>
                  <Input value={returnForm.form_type} onChange={(e) => setReturnForm((f) => ({ ...f, form_type: e.target.value }))} required />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Due Date</label>
                  <Input type="date" value={returnForm.due_date} onChange={(e) => setReturnForm((f) => ({ ...f, due_date: e.target.value }))} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowReturnModal(false)}>Cancel</Button>
                  <Button type="submit">Create</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {showOrganizerModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader><CardTitle>New Tax Organizer</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleCreateOrganizer} className="space-y-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Client</label>
                  <select
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={organizerForm.client_id}
                    onChange={(e) => setOrganizerForm((f) => ({ ...f, client_id: e.target.value }))}
                    required
                  >
                    <option value="">Select client</option>
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Tax Year</label>
                  <Input type="number" value={organizerForm.tax_year} onChange={(e) => setOrganizerForm((f) => ({ ...f, tax_year: parseInt(e.target.value) || 0 }))} required />
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowOrganizerModal(false)}>Cancel</Button>
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
