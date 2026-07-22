import { useState, useEffect } from 'react'
import { Search, Mail, CheckSquare, ChevronLeft } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiFetch } from '@/api/client'
import type { EmailMessage } from '@/types'

export function InboxPage() {
  const [emails, setEmails] = useState<EmailMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedEmail, setSelectedEmail] = useState<EmailMessage | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await apiFetch<EmailMessage[]>('/inbox/')
      setEmails(data)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleMarkRead = async (id: string) => {
    await apiFetch(`/inbox/${id}/read`, { method: 'PUT' })
    load()
  }

  const handleConvertToTask = async (id: string) => {
    await apiFetch(`/inbox/${id}/convert-task`, { method: 'POST' })
    load()
  }

  const handleSelect = async (email: EmailMessage) => {
    setSelectedEmail(email)
    if (!email.is_read) {
      await handleMarkRead(email.id)
    }
  }

  const filtered = emails.filter((e) =>
    e.subject.toLowerCase().includes(search.toLowerCase()) ||
    e.from_address.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="space-y-4">
        <div>
          <div className="skeleton h-8 w-32 rounded-lg" />
          <div className="skeleton h-4 w-48 rounded-lg mt-2" />
        </div>
        <div className="skeleton h-10 w-80 rounded-xl" />
        <div className="skeleton h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (selectedEmail) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => setSelectedEmail(null)}>
            <ChevronLeft className="w-4 h-4 mr-1" /> Back
          </Button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{selectedEmail.subject}</h1>
            <p className="text-sm text-muted-foreground">
              From: {selectedEmail.from_address}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={() => handleConvertToTask(selectedEmail.id)}>
            <CheckSquare className="w-4 h-4 mr-1" /> Convert to Task
          </Button>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-sm text-muted-foreground mb-4">
              {new Date(selectedEmail.received_at).toLocaleString()}
              {selectedEmail.to_address.length > 0 && (
                <> · To: {selectedEmail.to_address.join(', ')}</>
              )}
            </div>
            <div className="prose prose-sm max-w-none">
              <div
                className="text-sm whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: selectedEmail.body_html || selectedEmail.body_text }}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Inbox</h1>
        <p className="text-muted-foreground mt-1">Unified team email inbox.</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search emails..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {emails.length === 0 ? (
        <Card className="p-12 text-center">
          <Mail className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No emails yet</h3>
          <p className="text-muted-foreground">Connect an email account to start receiving emails.</p>
        </Card>
      ) : (
        <Card>
          <div className="divide-y">
            {filtered.map((email) => (
              <div
                key={email.id}
                className={`p-4 hover:bg-muted/50 transition-colors cursor-pointer ${!email.is_read ? 'bg-primary/5' : ''}`}
                onClick={() => handleSelect(email)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {!email.is_read && <div className="w-2 h-2 rounded-full bg-primary shrink-0" />}
                      <span className={`font-medium text-sm ${!email.is_read ? '' : 'text-muted-foreground'}`}>
                        {email.from_address}
                      </span>
                    </div>
                    <h3 className={`text-sm ${!email.is_read ? 'font-medium' : 'text-muted-foreground'}`}>
                      {email.subject}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                      {email.body_text.substring(0, 120)}
                    </p>
                  </div>
                  <div className="text-xs text-muted-foreground shrink-0 ml-4">
                    {new Date(email.received_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
