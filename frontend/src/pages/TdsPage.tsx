import { useState, useEffect } from 'react'
import { apiFetch } from '@/api/client'
import type { TdsRegistration, TdsDeduction, TdsReturn } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { Input } from '@/components/ui/input'
import { Landmark, Plus, Search } from 'lucide-react'

type Tab = 'registrations' | 'deductions' | 'returns'

export function TdsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('deductions')
  const [deductions, setDeductions] = useState<TdsDeduction[]>([])
  const [registrations, setRegistrations] = useState<TdsRegistration[]>([])
  const [returns, setReturns] = useState<TdsReturn[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => { load() }, [activeTab])

  async function load() {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'registrations':
          setRegistrations(await apiFetch('/tds/registrations'))
          break
        case 'deductions':
          setDeductions(await apiFetch('/tds/deductions'))
          break
        case 'returns':
          setReturns(await apiFetch('/tds/returns'))
          break
      }
    } finally {
      setLoading(false)
    }
  }



  const tabs: { key: Tab; label: string }[] = [
    { key: 'registrations', label: 'TAN Registrations' },
    { key: 'deductions', label: 'TDS Deductions' },
    { key: 'returns', label: 'TDS Returns' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Landmark className="w-6 h-6" />
          <h1 className="text-2xl font-bold">TDS / TCS Management</h1>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1" />
          {activeTab === 'deductions' ? 'Add Deduction' : activeTab === 'registrations' ? 'Add TAN' : 'Create Return'}
        </Button>
      </div>

      <div className="flex items-center justify-between border-b pb-2">
        <div className="flex gap-4">
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
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {activeTab === 'registrations' && (
        <div className="grid gap-4 md:grid-cols-2">
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="skeleton h-48 rounded-xl" />
              <div className="skeleton h-48 rounded-xl" />
            </div>
          ) : registrations.length === 0 ? (
            <Card className="md:col-span-2">
              <CardContent className="py-8 text-center text-muted-foreground">
                No TAN registrations yet. Add a TAN to start tracking TDS.
              </CardContent>
            </Card>
          ) : (
            registrations.map((reg) => (
              <Card key={reg.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-mono">{reg.tan}</CardTitle>
                    <StatusBadge status={reg.is_active ? 'active' : 'inactive'} />
                  </div>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  <p><span className="text-muted-foreground">PAN:</span> {reg.pan_of_deductor}</p>
                  <p><span className="text-muted-foreground">Name:</span> {reg.legal_name}</p>
                  <p><span className="text-muted-foreground">Role:</span> {reg.is_deductor ? 'Deductor' : ''}{reg.is_collector ? ' / Collector' : ''}</p>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {activeTab === 'deductions' && (
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="skeleton h-64 w-full" />
            ) : deductions.length === 0 ? (
              <p className="p-6 text-center text-muted-foreground">No TDS deductions recorded yet.</p>
            ) : (
              <div className="rounded-xl border overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Section</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Deductee</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">PAN</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Payment</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Rate</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">TDS</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Period</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {deductions.map((d) => (
                      <tr key={d.id} className="hover:bg-accent/50 transition-colors">
                        <td className="p-3 font-mono text-sm font-medium">{d.section}</td>
                        <td className="p-3 text-sm">{d.deductee_name}</td>
                        <td className="p-3 font-mono text-sm">{d.deductee_pan}</td>
                        <td className="p-3 text-sm">₹{d.payment_amount.toLocaleString()}</td>
                        <td className="p-3 text-sm">{d.tds_rate}%</td>
                        <td className="p-3 text-sm font-medium">₹{d.total_tds.toLocaleString()}</td>
                        <td className="p-3 text-sm">{d.financial_year} {d.quarter}</td>
                        <td className="p-3">
                          <StatusBadge status={d.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'returns' && (
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="skeleton h-64 w-full" />
            ) : returns.length === 0 ? (
              <p className="p-6 text-center text-muted-foreground">No TDS returns filed yet.</p>
            ) : (
              <div className="rounded-xl border overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Form</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Period</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">FY</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Due Date</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Deductions</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">TDS Amount</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                      <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Ack</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {returns.map((r) => (
                      <tr key={r.id} className="hover:bg-accent/50 transition-colors">
                        <td className="p-3 text-sm font-medium">{r.form_type}</td>
                        <td className="p-3 text-sm">{r.quarter}</td>
                        <td className="p-3 text-sm">{r.financial_year}</td>
                        <td className="p-3 text-sm">{r.due_date}</td>
                        <td className="p-3 text-sm">{r.total_deductions}</td>
                        <td className="p-3 text-sm">₹{r.total_tds_amount.toLocaleString()}</td>
                        <td className="p-3">
                          <StatusBadge status={r.status} />
                        </td>
                        <td className="p-3 text-xs font-mono">{r.acknowledgement || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
