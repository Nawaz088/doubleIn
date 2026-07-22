import * as React from 'react'
import { apiFetch } from '@/api/client'
import type { GstRegistration, HsnSacCode, GstInvoice, GstReturn, GstInvoiceLine } from '@/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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

  function getStatusBadge(status: string) {
    const variants: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      draft: 'bg-yellow-100 text-yellow-800',
      final: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      filed: 'bg-green-100 text-green-800',
      error: 'bg-red-100 text-red-800',
    }
    return variants[status] || 'bg-gray-100 text-gray-800'
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
        <Button onClick={() => setShowForm(true)}>
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
            <p className="text-muted-foreground">Loading...</p>
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
                    <Badge className={getStatusBadge(reg.status)}>{reg.status}</Badge>
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
            <p className="text-muted-foreground">Loading...</p>
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
                      <Badge variant="outline">{code.type.toUpperCase()}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm mb-2">{code.description}</p>
                    <div className="flex gap-2 text-sm">
                      <Badge className={code.gst_rate === 0 ? 'bg-gray-100' : 'bg-blue-100 text-blue-800'}>
                        {code.gst_rate}% GST
                      </Badge>
                      {code.cess_rate > 0 && (
                        <Badge className="bg-orange-100 text-orange-800">
                          {code.cess_rate}% Cess
                        </Badge>
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
            <p className="text-muted-foreground">Loading...</p>
          ) : invoices.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No GST invoices yet. Create an invoice to get started.
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-0">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3 text-xs font-medium text-muted-foreground">Invoice #</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Date</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Customer</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Taxable</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">GST</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Total</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Status</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">IRN</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoices.map((inv) => (
                      <tr key={inv.id} className="border-b last:border-0 hover:bg-accent/50">
                        <td className="p-3 font-mono text-sm">{inv.invoice_number}</td>
                        <td className="p-3 text-sm">{inv.invoice_date}</td>
                        <td className="p-3 text-sm">{inv.customer_name}</td>
                        <td className="p-3 text-sm">₹{inv.total_taxable_value.toLocaleString()}</td>
                        <td className="p-3 text-sm">
                          ₹{(inv.total_cgst + inv.total_sgst + inv.total_igst).toLocaleString()}
                        </td>
                        <td className="p-3 text-sm font-medium">₹{inv.total_invoice_value.toLocaleString()}</td>
                        <td className="p-3">
                          <Badge className={getStatusBadge(inv.status)}>{inv.status}</Badge>
                        </td>
                        <td className="p-3 text-xs">
                          {inv.irn_status === 'generated' ? (
                            <Badge className="bg-green-100 text-green-800">IRN Done</Badge>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'returns' && (
        <div className="space-y-4">
          {loading ? (
            <p className="text-muted-foreground">Loading...</p>
          ) : returns.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No GST returns yet. Create a return filing to track.
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-0">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3 text-xs font-medium text-muted-foreground">Return Type</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Period</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">FY</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Due Date</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Net Payable</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">Status</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground">ARN</th>
                    </tr>
                  </thead>
                  <tbody>
                    {returns.map((ret) => (
                      <tr key={ret.id} className="border-b last:border-0 hover:bg-accent/50">
                        <td className="p-3 text-sm font-medium">{ret.return_type}</td>
                        <td className="p-3 text-sm">{ret.return_period}</td>
                        <td className="p-3 text-sm">{ret.financial_year}</td>
                        <td className="p-3 text-sm">{ret.due_date}</td>
                        <td className="p-3 text-sm">₹{ret.net_payable.toLocaleString()}</td>
                        <td className="p-3">
                          <Badge className={getStatusBadge(ret.status)}>{ret.status}</Badge>
                        </td>
                        <td className="p-3 text-xs font-mono">{ret.arn || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
