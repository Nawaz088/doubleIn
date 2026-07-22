import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { scorecardApi } from '@/api/scorecards'

export function ScorecardBuilderPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const sc = await scorecardApi.create({
        name,
        period_start: periodStart,
        period_end: periodEnd,
      })
      navigate(`/scorecards/${sc.id}`)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create scorecard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Scorecard</h1>
          <p className="text-muted-foreground mt-1">
            Create a scorecard to track KPIs for a board meeting or review period.
          </p>
        </div>
      </div>

      <Card>
        <form onSubmit={handleCreate}>
          <CardContent className="space-y-4 pt-6">
            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">{error}</div>
            )}
            <div>
              <label className="text-sm font-medium block mb-1">Scorecard Name</label>
              <Input
                placeholder="Q3 2026 Board Review"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium block mb-1">Period Start</label>
                <Input
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Period End</label>
                <Input
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="pt-4 flex gap-2">
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Scorecard'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => navigate('/scorecards')}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </form>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>What is a Scorecard?</CardTitle>
          <CardDescription>Your board-meeting companion</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <ul className="space-y-2 list-disc list-inside">
            <li>All pre-built KPIs (Tasks Completed, Closes On Time %, etc.) are auto-populated</li>
            <li>Add manual KPIs like Revenue Per Client or Client Satisfaction</li>
            <li>Use Meeting View for fullscreen projector display during board meetings</li>
            <li>Track action items, attendees, and comments all in one place</li>
            <li>Publish to freeze the scorecard and export as PDF</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
