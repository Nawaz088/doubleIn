import { useState, useEffect } from 'react'
import { apiFetch } from '@/api/client'
import type { ChartOfAccount } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Upload } from 'lucide-react'

const accountTypeColors: Record<string, string> = {
  equity: 'bg-purple-100 text-purple-800',
  assets: 'bg-green-100 text-green-800',
  liabilities: 'bg-orange-100 text-orange-800',
  income: 'bg-blue-100 text-blue-800',
  expenses: 'bg-red-100 text-red-800',
}

export function ChartOfAccountsPage() {
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [])

  async function load() {
    setLoading(true)
    try {
      setAccounts(await apiFetch('/india/chart-of-accounts'))
    } finally {
      setLoading(false)
    }
  }

  async function seedScheduleIII() {
    await apiFetch('/india/chart-of-accounts/seed', { method: 'POST' })
    load()
  }

  const grouped = accounts.reduce<Record<string, ChartOfAccount[]>>((acc, acct) => {
    const t = acct.type || 'other'
    if (!acc[t]) acc[t] = []
    acc[t].push(acct)
    return acc
  }, {})

  const sectionOrder = ['equity', 'assets', 'liabilities', 'income', 'expenses']
  const sectionLabels: Record<string, string> = {
    equity: 'Equity & Liabilities',
    assets: 'Assets',
    liabilities: 'Liabilities',
    income: 'Income',
    expenses: 'Expenses',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookOpen className="w-6 h-6" />
          <h1 className="text-2xl font-bold">Chart of Accounts (Schedule III)</h1>
        </div>
        <Button variant="outline" size="sm" className="gap-2" onClick={seedScheduleIII}>
          <Upload className="w-4 h-4" />
          Seed Schedule III
        </Button>
      </div>

      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : accounts.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-muted-foreground mb-4">No chart of accounts yet.</p>
            <Button onClick={seedScheduleIII}>Seed Schedule III Accounts</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sectionOrder.map((section) => {
            const items = grouped[section] || []
            if (items.length === 0) return null
            return (
              <Card key={section}>
                <CardHeader>
                  <CardTitle className="text-base">{sectionLabels[section] || section}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1">
                    {items.map((acct) => (
                      <div
                        key={acct.id}
                        className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-accent/50"
                      >
                        <div className="flex items-center gap-3">
                          <code className="text-xs text-muted-foreground w-16">{acct.code}</code>
                          <span className="text-sm">{acct.name}</span>
                        </div>
                        <Badge className={accountTypeColors[acct.type] || ''}>
                          {acct.type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
