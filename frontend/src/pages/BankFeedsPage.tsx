import { useState, useEffect } from 'react'
import {
  Search, Filter, Check, X, ChevronDown, Plus, Landmark,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import { cn } from '@/lib/utils'
import type { BankTransaction, ClassificationRule, Client } from '@/types'

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' | 'danger' }> = {
  pending: { label: 'Pending', variant: 'outline' },
  matched: { label: 'Matched', variant: 'success' },
  classified: { label: 'Classified', variant: 'warning' },
  needs_review: { label: 'Needs Review', variant: 'danger' },
  posted: { label: 'Posted', variant: 'success' },
}

const tierConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'outline' }> = {
  match: { label: 'Match', variant: 'success' },
  rule: { label: 'Rule', variant: 'warning' },
  manual: { label: 'Manual', variant: 'outline' },
  unclassified: { label: 'Unclassified', variant: 'outline' },
}

export function BankFeedsPage() {
  const [transactions, setTransactions] = useState<BankTransaction[]>([])
  const [rules, setRules] = useState<ClassificationRule[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'transactions' | 'rules'>('transactions')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [tierFilter, setTierFilter] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const load = async () => {
    setLoading(true)
    try {
      const [txns, rls] = await Promise.all([
        apiFetch<BankTransaction[]>('/bank-feeds/transactions'),
        apiFetch<ClassificationRule[]>('/bank-feeds/rules'),
      ])
      setTransactions(txns)
      setRules(rls)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleApprove = async (id: string) => {
    await apiFetch(`/bank-feeds/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status: 'approved' }),
    })
    load()
  }

  const handleBulkApprove = async () => {
    await apiFetch('/bank-feeds/transactions/bulk', {
      method: 'POST',
      body: JSON.stringify({ ids: Array.from(selected), status: 'approved' }),
    })
    setSelected(new Set())
    load()
  }

  const handleClassify = async (id: string, category: string) => {
    await apiFetch(`/bank-feeds/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ category, status: 'classified' }),
    })
    load()
  }

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const filtered = transactions.filter((t) => {
    if (search && !t.description.toLowerCase().includes(search.toLowerCase()) && !t.vendor_name?.toLowerCase().includes(search.toLowerCase())) return false
    if (statusFilter && t.status !== statusFilter) return false
    if (tierFilter && t.classification_tier !== tierFilter) return false
    return true
  })

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
          <h1 className="text-3xl font-bold tracking-tight">Bank Feeds</h1>
          <p className="text-muted-foreground mt-1">Reconcile and classify bank transactions.</p>
        </div>
      </div>

      <div className="flex gap-1 border-b">
        <button
          onClick={() => setActiveTab('transactions')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'transactions' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Transactions
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'rules' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          Classification Rules
        </button>
      </div>

      {activeTab === 'transactions' && (
        <>
          <div className="flex items-center gap-3 flex-wrap">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search transactions..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
            </div>
            <select
              className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="matched">Matched</option>
              <option value="classified">Classified</option>
              <option value="needs_review">Needs Review</option>
              <option value="posted">Posted</option>
            </select>
            <select
              className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value)}
            >
              <option value="">All Tiers</option>
              <option value="match">Match</option>
              <option value="rule">Rule</option>
              <option value="manual">Manual</option>
              <option value="unclassified">Unclassified</option>
            </select>
          </div>

          {selected.size > 0 && (
            <Card className="p-3 flex items-center gap-3">
              <span className="text-sm">{selected.size} selected</span>
              <Button size="sm" onClick={handleBulkApprove}>Approve Selected</Button>
              <Button size="sm" variant="outline" onClick={() => setSelected(new Set())}>Clear</Button>
            </Card>
          )}

          {filtered.length === 0 ? (
            <Card className="p-12 text-center">
              <Landmark className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No transactions</h3>
              <p className="text-muted-foreground">Connect a bank account to see transactions here.</p>
            </Card>
          ) : (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="p-3 text-sm font-medium text-muted-foreground w-10">
                        <input type="checkbox" onChange={(e) => {
                          if (e.target.checked) setSelected(new Set(filtered.map((t) => t.id)))
                          else setSelected(new Set())
                        }} />
                      </th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Date</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Description</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Amount</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Vendor</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Category</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Tier</th>
                      <th className="p-3 text-sm font-medium text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((t) => (
                      <tr key={t.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                        <td className="p-3">
                          <input type="checkbox" checked={selected.has(t.id)} onChange={() => toggleSelect(t.id)} />
                        </td>
                        <td className="p-3 text-sm">{new Date(t.date).toLocaleDateString()}</td>
                        <td className="p-3 text-sm max-w-[200px] truncate">{t.description}</td>
                        <td className={cn('p-3 text-sm font-mono', t.amount < 0 ? 'text-red-400' : 'text-emerald-400')}>
                          ${Math.abs(t.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="p-3 text-sm text-muted-foreground">{t.vendor_name || '—'}</td>
                        <td className="p-3 text-sm text-muted-foreground">{t.category || '—'}</td>
                        <td className="p-3">
                          <Badge variant={statusConfig[t.status]?.variant || 'outline'}>
                            {statusConfig[t.status]?.label || t.status}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge variant={tierConfig[t.classification_tier]?.variant || 'outline'}>
                            {tierConfig[t.classification_tier]?.label || t.classification_tier}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1">
                            {t.status === 'needs_review' && (
                              <Button variant="ghost" size="sm" onClick={() => handleApprove(t.id)}>
                                <Check className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
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

      {activeTab === 'rules' && (
        <>
          {rules.length === 0 ? (
            <Card className="p-12 text-center">
              <Filter className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No classification rules</h3>
              <p className="text-muted-foreground">Create rules to auto-classify transactions.</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {rules.map((rule) => (
                <Card key={rule.id}>
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Rule #{rule.priority}</span>
                        <Badge variant={rule.is_active ? 'success' : 'outline'}>
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        Conditions: {JSON.stringify(rule.conditions)} | Actions: {JSON.stringify(rule.actions)}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
