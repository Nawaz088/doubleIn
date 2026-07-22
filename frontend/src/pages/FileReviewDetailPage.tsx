import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Check, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { ReviewFinding } from '@/types'

const findingStatusConfig: Record<string, { label: string; variant: 'success' | 'outline' | 'warning' }> = {
  open: { label: 'Open', variant: 'warning' },
  resolved: { label: 'Resolved', variant: 'success' },
  ignored: { label: 'Ignored', variant: 'outline' },
}

export function FileReviewDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [findings, setFindings] = useState<ReviewFinding[]>([])
  const [report, setReport] = useState<{ name: string } | null>(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await apiFetch<{ report: { name: string }; findings: ReviewFinding[] }>(`/file-review/reports/${id}`)
      setReport(data.report)
      setFindings(data.findings || [])
    } catch {
      try {
        const f = await apiFetch<ReviewFinding[]>(`/file-review/reports/${id}/findings`)
        setFindings(f)
      } catch {}
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handleResolve = async (findingId: string) => {
    if (!id) return
    await apiFetch(`/file-review/reports/${id}/findings/${findingId}/resolve`, { method: 'POST' })
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
      <div className="flex items-center gap-4">
        <Link to="/file-review" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">
            {report?.name || 'Review Report'}
          </h1>
          <p className="text-muted-foreground mt-1">{findings.length} findings</p>
        </div>
      </div>

      {findings.length === 0 ? (
        <Card className="p-12 text-center">
          <Check className="w-12 h-12 mx-auto text-emerald-400 mb-4" />
          <h3 className="text-lg font-medium mb-2">No findings</h3>
          <p className="text-muted-foreground">No issues found in this review report.</p>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="p-3 text-sm font-medium text-muted-foreground">Transaction</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Date</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Amount</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Issue</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Suggested Action</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="p-3 text-sm font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {findings.map((f) => (
                  <tr key={f.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                    <td className="p-3 text-sm font-mono text-xs truncate max-w-[120px]">
                      {f.transaction_external_id}
                    </td>
                    <td className="p-3 text-sm">{new Date(f.transaction_date).toLocaleDateString()}</td>
                    <td className="p-3 text-sm font-mono">
                      ${f.transaction_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-3 text-sm max-w-[200px] truncate">{f.issue}</td>
                    <td className="p-3 text-sm text-muted-foreground max-w-[200px] truncate">
                      {f.suggested_action || '—'}
                    </td>
                    <td className="p-3">
                      <Badge variant={findingStatusConfig[f.status]?.variant || 'outline'}>
                        {findingStatusConfig[f.status]?.label || f.status}
                      </Badge>
                    </td>
                    <td className="p-3">
                      {f.status === 'open' && (
                        <Button variant="ghost" size="sm" onClick={() => handleResolve(f.id)}>
                          <Check className="w-4 h-4 mr-1" /> Resolve
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
