import { useState, useEffect } from 'react'
import { Save, Building2, CreditCard, Users, Bell, UserPlus, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/api/client'
import type { Organization } from '@/types'

interface TeamMember {
  id: string
  user_id: string
  email: string
  name: string
  role: string
  avatar_url: string | null
  is_active: boolean
  created_at: string
}

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'organization' | 'billing' | 'team' | 'notifications'>('organization')
  const [org, setOrg] = useState<Organization | null>(null)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ name: '', slug: '' })
  const [saving, setSaving] = useState(false)
  const [members, setMembers] = useState<TeamMember[]>([])
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('member')

  const load = async () => {
    setLoading(true)
    try {
      const [data, membersData] = await Promise.all([
        apiFetch<Organization>('/org/settings'),
        apiFetch<TeamMember[]>('/org/members'),
      ])
      setOrg(data)
      setForm({ name: data.name, slug: data.slug })
      setMembers(membersData)
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await apiFetch('/org/settings', {
        method: 'PUT',
        body: JSON.stringify(form),
      })
      load()
    } catch {} finally {
      setSaving(false)
    }
  }

  const handleInvite = async () => {
    if (!inviteEmail) return
    await apiFetch(`/org/members/invite?email=${encodeURIComponent(inviteEmail)}&role=${inviteRole}`, {
      method: 'POST',
    })
    setInviteEmail('')
  }

  const handleRemove = async (memberId: string) => {
    await apiFetch(`/org/members/${memberId}`, { method: 'DELETE' })
    setMembers(members.filter((m) => m.id !== memberId))
  }

  const handleRoleChange = async (memberId: string, role: string) => {
    await apiFetch(`/org/members/${memberId}?role=${role}`, { method: 'PUT' })
    setMembers(members.map((m) => m.id === memberId ? { ...m, role } : m))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  const tabs = [
    { key: 'organization' as const, label: 'Organization', icon: Building2 },
    { key: 'billing' as const, label: 'Billing', icon: CreditCard },
    { key: 'team' as const, label: 'Team', icon: Users },
    { key: 'notifications' as const, label: 'Notifications', icon: Bell },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your organization settings.</p>
      </div>

      <div className="flex gap-6">
        <div className="w-48 shrink-0 space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 w-full px-3 py-2 text-sm rounded-lg transition-colors ${
                  activeTab === tab.key
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        <div className="flex-1">
          {activeTab === 'organization' && (
            <Card>
              <CardHeader>
                <CardTitle>Organization Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 max-w-md">
                <div>
                  <label className="text-sm font-medium block mb-1">Organization Name</label>
                  <Input
                    value={form.name}
                    onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Slug</label>
                  <Input
                    value={form.slug}
                    onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                  />
                </div>
                <Button onClick={handleSave} disabled={saving} className="gap-2">
                  <Save className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </CardContent>
            </Card>
          )}

          {activeTab === 'billing' && (
            <Card className="p-12 text-center">
              <CreditCard className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Billing</h3>
              <p className="text-muted-foreground">Billing management coming soon.</p>
            </Card>
          )}

          {activeTab === 'team' && (
            <Card>
              <CardHeader>
                <CardTitle>Team Members ({members.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Email address"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="flex-1"
                  />
                  <select
                    className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    <option value="member">Member</option>
                    <option value="admin">Admin</option>
                  </select>
                  <Button size="sm" onClick={handleInvite} className="gap-1">
                    <UserPlus className="w-4 h-4" />
                    Invite
                  </Button>
                </div>
                <div className="space-y-2">
                  {members.map((m) => (
                    <div key={m.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold">
                          {m.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-sm">{m.name}</p>
                          <p className="text-xs text-muted-foreground">{m.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <select
                          className="flex h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                          value={m.role}
                          onChange={(e) => handleRoleChange(m.id, e.target.value)}
                        >
                          <option value="owner">Owner</option>
                          <option value="admin">Admin</option>
                          <option value="member">Member</option>
                        </select>
                        <Badge variant={m.is_active ? 'success' : 'outline'}>
                          {m.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button variant="ghost" size="icon" onClick={() => handleRemove(m.id)}>
                          <Trash2 className="w-3.5 h-3.5 text-muted-foreground" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card className="p-12 text-center">
              <Bell className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Notification Preferences</h3>
              <p className="text-muted-foreground">Notification settings coming soon.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
