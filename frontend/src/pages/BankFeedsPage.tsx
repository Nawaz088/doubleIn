import { useState, useEffect } from 'react'
import {
  Search, Filter, Check, Plus, Landmark,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import { cn } from '@/lib/utils'
import type { BankTransaction, ClassificationRule } from '@/types'

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
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="skeleton h-8 w-48 rounded-lg" />
            <div className="skeleton h-4 w-64 rounded-lg mt-2" />
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
              className="flex h-9 rounded-lg border bg-card pl-3 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
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
              className="flex h-9 rounded-lg border bg-card pl-3 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
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
            <div className="rounded-xl border overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider w-10">
                      <input type="checkbox" onChange={(e) => {
                        if (e.target.checked) setSelected(new Set(filtered.map((t) => t.id)))
                        else setSelected(new Set())
                      }} />
                    </th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Date</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Description</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Amount</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Vendor</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Category</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Tier</th>
                    <th className="p-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.map((t) => (
                    <tr key={t.id} className="hover:bg-accent/50 transition-colors">
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
                        <StatusBadge status={t.status} />
                      </td>
                      <td className="p-3">
                        <StatusBadge status={t.classification_tier} />
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
                        <StatusBadge status={rule.is_active ? 'active' : 'inactive'} />
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
