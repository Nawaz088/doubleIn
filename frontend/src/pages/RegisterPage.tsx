import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'

export function RegisterPage() {
  const [form, setForm] = useState({ org_name: '', slug: '', name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [field]: e.target.value })

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">DoubleHQ</CardTitle>
          <CardDescription>Create your account</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">{error}</div>
            )}
            <div>
              <label className="text-sm font-medium block mb-1">Organization Name</label>
              <Input value={form.org_name} onChange={update('org_name')} required />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Organization Slug</label>
              <Input value={form.slug} onChange={update('slug')} placeholder="my-firm" required />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Your Name</label>
              <Input value={form.name} onChange={update('name')} required />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Email</label>
              <Input type="email" value={form.email} onChange={update('email')} required />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Password</label>
              <Input type="password" value={form.password} onChange={update('password')} required />
            </div>
          </CardContent>
          <CardFooter className="flex-col gap-3">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating...' : 'Create account'}
            </Button>
            <p className="text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline">Sign in</Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
