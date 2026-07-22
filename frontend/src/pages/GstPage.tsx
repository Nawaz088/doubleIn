import * as React from 'react'
import { apiFetch } from '@/api/client'
import type { GstRegistration, HsnSacCode, GstInvoice, GstReturn } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/ui/status-badge'
import { Input } from '@/components/ui/input'
import { IndianRupee } from 'lucide-react'

type Tab = 'registrations' | 'hsn-sac' | 'invoices' | 'returns'

export function GstPage() {
  const [activeTab, setActiveTab] = React.useState<Tab>('registrations')
  const [registrations, setRegistrations] = React.useState<GstRegistration[]>([])
  const [hsnCodes, setHsnCodes] = React.useState<HsnSacCode[]>([])
  const [invoices, setInvoices] = React.useState<GstInvoice[]>([])
  const [returns, setReturns] = React.useState<GstReturn[]>([])
  const [loading, setLoading] = React.useState(true)
  const [showForm, setShowForm] = React.useState(false)

  React.useEffect(() => {
    loadData()
  }, [activeTab])

  async function loadData() {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'registrations':
          setRegistrations(await apiFetch('/gst/registrations'))
          break
        case 'hsn-sac':
          setHsnCodes(await apiFetch('/gst/hsn-sac'))
          break
        case 'invoices':
          setInvoices(await apiFetch('/gst/invoices'))
          break
        case 'returns':
          setReturns(await apiFetch('/gst/returns'))
          break
      }
    } finally {
      setLoading(false)
    }
  }



  const tabs: { key: Tab; label: string }[] = [
    { key: 'registrations', label: 'Registrations' },
    { key: 'hsn-sac', label: 'HSN/SAC Codes' },
    { key: 'invoices', label: 'Invoices' },
    { key: 'returns', label: 'Returns' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <IndianRupee className="w-6 h-6" />
          <h1 className="text-2xl font-bold">GST Compliance</h1>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          {activeTab === 'registrations' && 'Add GSTIN'}
          {activeTab === 'hsn-sac' && 'Add HSN/SAC'}
          {activeTab === 'invoices' && 'Create Invoice'}
          {activeTab === 'returns' && 'Create Return'}
        </Button>
      </div>

      <div className="flex gap-4 border-b pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'registrations' && (
        <div className="space-y-4">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="skeleton h-48 rounded-xl" />
              <div className="skeleton h-48 rounded-xl" />
            </div>
          ) : registrations.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No GST registrations yet. Add a client's GSTIN to get started.
              </CardContent>
            </Card>
          ) : (
            registrations.map((reg) => (
              <Card key={reg.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-mono">{reg.gstin}</CardTitle>
                    <StatusBadge status={reg.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Legal Name:</span>
                      <p className="font-medium">{reg.legal_name}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Trade Name:</span>
                      <p className="font-medium">{reg.trade_name || '-'}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">State:</span>
                      <p className="font-medium">{reg.state_name}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Type:</span>
                      <p className="font-medium capitalize">{reg.registration_type}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Filing Frequency:</span>
                      <p className="font-medium capitalize">{reg.filing_frequency}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Composition:</span>
                      <p className="font-medium">{reg.is_composition ? 'Yes' : 'No'}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">E-Invoice:</span>
                      <p className="font-medium">{reg.e_invoice_enabled ? 'Enabled' : 'Disabled'}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">E-Waybill:</span>
                      <p className="font-medium">{reg.e_waybill_enabled ? 'Enabled' : 'Disabled'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'hsn-sac' && (
        <div className="space-y-4">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="skeleton h-32 rounded-xl" />
              <div className="skeleton h-32 rounded-xl" />
              <div className="skeleton h-32 rounded-xl" />
            </div>
          ) : hsnCodes.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No HSN/SAC codes configured. Add codes to enable GST auto-calculation.
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {hsnCodes.map((code) => (
                <Card key={code.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg font-mono">{code.code}</CardTitle>
                      <StatusBadge status="todo" label={code.type.toUpperCase()} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm mb-2">{code.description}</p>
                    <div className="flex gap-2 text-sm">
                      <StatusBadge status={code.gst_rate === 0 ? 'inactive' : 'active'} label={`${code.gst_rate}% GST`} />
                      {code.cess_rate > 0 && (
                        <StatusBadge status="pending" label={`${code.cess_rate}% Cess`} />
                      )}
                    </div>
                    {code.chapter && (
                      <p className="text-xs text-muted-foreground mt-2">Chapter {code.chapter}</p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'invoices' && (
        <div className="space-y-4">
          {loading ? (
            <div className="skeleton h-64 w-full rounded-xl" />
          ) : invoices.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No GST invoices yet. Create an invoice to get started.
              </CardContent>
            </Card>
          ) : (
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Invoice #</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Date</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Customer</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Taxable</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">GST</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Total</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">IRN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {invoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3 font-mono text-sm">{inv.invoice_number}</td>
                      <td className="p-3 text-sm">{inv.invoice_date}</td>
                      <td className="p-3 text-sm">{inv.customer_name}</td>
                      <td className="p-3 text-sm">₹{inv.total_taxable_value.toLocaleString()}</td>
                      <td className="p-3 text-sm">
                        ₹{(inv.total_cgst + inv.total_sgst + inv.total_igst).toLocaleString()}
                      </td>
                      <td className="p-3 text-sm font-medium">₹{inv.total_invoice_value.toLocaleString()}</td>
                      <td className="p-3">
                        <StatusBadge status={inv.status} />
                      </td>
                      <td className="p-3 text-xs">
                        {inv.irn_status === 'generated' ? (
                          <StatusBadge status="filed" label="IRN Done" />
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'returns' && (
        <div className="space-y-4">
          {loading ? (
            <div className="skeleton h-64 w-full rounded-xl" />
          ) : returns.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No GST returns yet. Create a return filing to track.
              </CardContent>
            </Card>
          ) : (
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Return Type</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Period</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">FY</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Due Date</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Net Payable</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">ARN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {returns.map((ret) => (
                    <tr key={ret.id} className="hover:bg-accent/50 transition-colors">
                      <td className="p-3 text-sm font-medium">{ret.return_type}</td>
                      <td className="p-3 text-sm">{ret.return_period}</td>
                      <td className="p-3 text-sm">{ret.financial_year}</td>
                      <td className="p-3 text-sm">{ret.due_date}</td>
                      <td className="p-3 text-sm">₹{ret.net_payable.toLocaleString()}</td>
                      <td className="p-3">
                        <StatusBadge status={ret.status} />
                      </td>
                      <td className="p-3 text-xs font-mono">{ret.arn || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
