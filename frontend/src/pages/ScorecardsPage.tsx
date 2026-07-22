import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FileText, Calendar, MoreVertical } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { scorecardApi } from '@/api/scorecards'
import type { Scorecard } from '@/types'

const frequencyLabels: Record<string, string> = {
  weekly: 'Weekly',
  monthly: 'Monthly',
  quarterly: 'Quarterly',
  yearly: 'Yearly',
}

export function ScorecardsPage() {
  const [scorecards, setScorecards] = useState<Scorecard[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    scorecardApi.list()
      .then(setScorecards)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="skeleton h-8 w-48 rounded-lg" />
            <div className="skeleton h-4 w-64 rounded-lg mt-2" />
          </div>
          <div className="flex gap-2">
            <div className="skeleton h-9 w-28 rounded-lg" />
            <div className="skeleton h-9 w-32 rounded-lg" />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="skeleton h-36 rounded-xl" />
          <div className="skeleton h-36 rounded-xl" />
          <div className="skeleton h-36 rounded-xl" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Scorecards</h1>
          <p className="text-muted-foreground mt-1">
            Track KPIs, run board meetings, and manage action items.
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/scorecards/definitions">
            <Button variant="outline" size="sm">Manage KPIs</Button>
          </Link>
          <Link to="/scorecards/new">
            <Button size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              New Scorecard
            </Button>
          </Link>
        </div>
      </div>

      {scorecards.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No scorecards yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first scorecard to track KPIs and run board meetings.
          </p>
          <Link to="/scorecards/new">
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              Create Scorecard
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {scorecards.map((sc) => (
            <Link key={sc.id} to={`/scorecards/${sc.id}`}>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
                <CardContent className="p-6 space-y-3">
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-lg">{sc.name}</h3>
                    <StatusBadge status={sc.status} />
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5" />
                    {sc.period_start} ― {sc.period_end}
                  </div>
                  {sc.meeting_date && (
                    <div className="text-xs text-muted-foreground">
                      Meeting: {new Date(sc.meeting_date).toLocaleDateString()}
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
