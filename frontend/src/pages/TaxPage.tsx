import { useState, useEffect } from 'react'
import { Plus, FileText, Calendar, ClipboardList, FileCheck, User, IndianRupee, Building2, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import type { TaxReturn, TaxOrganizer, Client, ItrFiling, McaFiling, AdvanceTaxInstallment } from '@/types'

export function TaxPage() {
  const [returns, setReturns] = useState<TaxReturn[]>([])
  const [organizers, setOrganizers] = useState<TaxOrganizer[]>([])
  const [itrFilings, setItrFilings] = useState<ItrFiling[]>([])
  const [mcaFilings, setMcaFilings] = useState<McaFiling[]>([])
  const [advanceTax, setAdvanceTax] = useState<AdvanceTaxInstallment[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'returns' | 'organizers' | 'filings' | 'itr' | 'mca' | 'advance-tax'>('returns')
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
      const [r, o, c, itr, mca, at] = await Promise.all([
        apiFetch<TaxReturn[]>('/tax/returns'),
        apiFetch<TaxOrganizer[]>('/tax/organizers'),
        apiFetch<Client[]>('/clients/'),
        apiFetch<ItrFiling[]>('/itr/filings'),
        apiFetch<McaFiling[]>('/itr/mca'),
        apiFetch<AdvanceTaxInstallment[]>('/itr/advance-tax'),
      ])
      setReturns(r)
      setOrganizers(o)
      setClients(c)
      setItrFilings(itr)
      setMcaFilings(mca)
      setAdvanceTax(at)
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
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="skeleton h-8 w-32 rounded-lg" />
            <div className="skeleton h-4 w-48 rounded-lg mt-2" />
          </div>
        </div>
        <div className="skeleton h-10 w-full rounded-xl" />
        <div className="skeleton h-64 w-full rounded-xl" />
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

      <div className="flex gap-1 border-b overflow-x-auto">
        {(['returns', 'organizers', 'filings', 'itr', 'mca', 'advance-tax'] as const).map((tab) => {
          const icons: Record<string, React.ElementType> = {
            returns: FileText,
            organizers: ClipboardList,
            filings: FileCheck,
            itr: IndianRupee,
            mca: Building2,
            'advance-tax': Calendar,
          }
          const labels: Record<string, string> = {
            returns: 'Tax Returns',
            organizers: 'Organizers',
            filings: 'Signatures',
            itr: 'ITR Filings',
            mca: 'MCA/ROC',
            'advance-tax': 'Advance Tax',
          }
          const Icon = icons[tab]
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors shrink-0 ${
                activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="w-4 h-4" />
              {labels[tab]}
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
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Year</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Form</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Due Date</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Assignee</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {returns.map((r) => (
                    <tr key={r.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3 text-sm">{r.tax_year}</td>
                      <td className="p-3 text-sm">{r.form_type}</td>
                      <td className="p-3">
                        <StatusBadge status={r.status} />
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
                    <StatusBadge status={o.status} />
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

      {activeTab === 'itr' && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              New ITR Filing
            </Button>
          </div>
          {itrFilings.length === 0 ? (
            <Card className="p-12 text-center">
              <IndianRupee className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No ITR filings</h3>
              <p className="text-muted-foreground">Track ITR-1 to ITR-7 filings for your clients.</p>
            </Card>
          ) : (
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Form</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">FY</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">AY</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Income</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Tax</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Refund</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Ack</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {itrFilings.map((f) => (
                    <tr key={f.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3 text-sm font-medium">{f.form_type}</td>
                      <td className="p-3 text-sm">{f.financial_year}</td>
                      <td className="p-3 text-sm">{f.assessment_year}</td>
                      <td className="p-3 text-sm">₹{f.gross_income.toLocaleString()}</td>
                      <td className="p-3 text-sm">₹{f.total_tax.toLocaleString()}</td>
                      <td className="p-3 text-sm text-emerald-600">₹{f.refund_amount.toLocaleString()}</td>
                      <td className="p-3">
                        <StatusBadge status={f.status} />
                      </td>
                      <td className="p-3 text-xs font-mono">{f.itr_acknowledgement || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'mca' && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              New MCA Filing
            </Button>
          </div>
          {mcaFilings.length === 0 ? (
            <Card className="p-12 text-center">
              <Building2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No MCA/ROC filings</h3>
              <p className="text-muted-foreground">Track AOC-4, MGT-7, and other MCA filings.</p>
            </Card>
          ) : (
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Form</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Company</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">FY</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Due</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Filed</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">SRN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {mcaFilings.map((f) => (
                    <tr key={f.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3 text-sm font-medium">{f.form_type}</td>
                      <td className="p-3 text-sm">{f.company_name}</td>
                      <td className="p-3 text-sm">{f.financial_year}</td>
                      <td className="p-3 text-sm">{f.due_date}</td>
                      <td className="p-3 text-sm">{f.filing_date || '-'}</td>
                      <td className="p-3">
                        <StatusBadge status={f.status} />
                      </td>
                      <td className="p-3 text-xs font-mono">{f.srn || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'advance-tax' && (
        <div className="space-y-4">
          {advanceTax.length === 0 ? (
            <Card className="p-12 text-center">
              <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No advance tax records</h3>
              <p className="text-muted-foreground">Track advance tax installments due on 15-Jun, 15-Sep, 15-Dec, 15-Mar.</p>
            </Card>
          ) : (
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Inst.</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">FY</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Due</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Amount Due</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Paid</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Balance</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {advanceTax.map((a) => (
                      <tr key={a.id} className="hover:bg-accent/50 transition-colors">
                        <td className="p-3 text-sm font-medium">#{a.installment_no}</td>
                        <td className="p-3 text-sm">{a.financial_year}</td>
                        <td className="p-3 text-sm">{a.due_date}</td>
                        <td className="p-3 text-sm">₹{a.amount_due.toLocaleString()}</td>
                        <td className="p-3 text-sm">₹{a.amount_paid.toLocaleString()}</td>
                        <td className="p-3 text-sm font-medium">₹{(a.amount_due - a.amount_paid).toLocaleString()}</td>
                        <td className="p-3">
                          <StatusBadge status={a.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
          )}
        </div>
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
