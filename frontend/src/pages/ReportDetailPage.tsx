import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Send, Plus, FileDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { apiFetch } from '@/api/client'
import type { ReportPackage, ReportSection } from '@/types'

const sectionLabels: Record<string, string> = {
  cover_sheet: 'Cover Sheet',
  executive_summary: 'Executive Summary',
  profit_loss: 'Profit & Loss',
  balance_sheet: 'Balance Sheet',
  cash_flow: 'Cash Flow',
  kpi_metrics: 'KPI Metrics',
  ap_aging: 'AP Aging',
  ar_aging: 'AR Aging',
  top_customers: 'Top Customers',
  top_vendors: 'Top Vendors',
  notes: 'Notes',
}

export function ReportDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [report, setReport] = useState<ReportPackage | null>(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await apiFetch<ReportPackage>(`/reports/${id}`)
      setReport(data)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handlePublish = async () => {
    if (!id) return
    await apiFetch(`/reports/${id}/publish`, { method: 'POST' })
    load()
  }

  const handleAddSection = async (sectionType: string) => {
    if (!id) return
    await apiFetch(`/reports/${id}/sections`, {
      method: 'POST',
      body: JSON.stringify({
        section_type: sectionType,
        config: {},
        sort_order: (report?.sections?.length || 0) + 1,
      }),
    })
    load()
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="skeleton h-5 w-5 rounded" />
          <div>
            <div className="skeleton h-8 w-64 rounded-lg" />
            <div className="skeleton h-4 w-48 rounded-lg mt-2" />
          </div>
        </div>
        <div className="skeleton h-24 w-full rounded-xl" />
        <div className="skeleton h-48 w-full rounded-xl" />
      </div>
    )
  }

  if (!report) return null

  const sections = report.sections || []

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/reports" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{report.name}</h1>
          <p className="text-muted-foreground">
            {report.period_start} ― {report.period_end}
          </p>
        </div>
        <StatusBadge status={report.status} />
        {report.status === 'draft' && (
          <Button size="sm" onClick={handlePublish}>
            <Send className="w-4 h-4 mr-1" /> Publish
          </Button>
        )}
        <Button variant="outline" size="sm">
          <FileDown className="w-4 h-4 mr-1" /> Export PDF
        </Button>
      </div>

      <div className="space-y-3">
        {sections
          .sort((a, b) => a.sort_order - b.sort_order)
          .map((section) => (
            <Card key={section.id}>
              <CardContent className="flex items-center justify-between py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center">
                    <span className="text-xs font-bold">{section.sort_order}</span>
                  </div>
                  <div>
                    <h3 className="font-medium">{sectionLabels[section.section_type] || section.section_type}</h3>
                    <p className="text-xs text-muted-foreground">{section.section_type.replace(/_/g, ' ')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
      </div>

      {sections.length === 0 && (
        <Card className="p-12 text-center">
          <Plus className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No sections yet</h3>
          <p className="text-muted-foreground mb-4">Add sections to build your report.</p>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle className="text-base">Add Section</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(sectionLabels).map(([key, label]) => (
              <Button
                key={key}
                variant="outline"
                size="sm"
                className="justify-start"
                onClick={() => handleAddSection(key)}
              >
                <Plus className="w-3 h-3 mr-2" />
                {label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
