import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { apiFetch } from '../api/client'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { org_name: string; slug: string; email: string; password: string; name: string }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const data = await apiFetch<User>('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (email: string, password: string) => {
    const data = await apiFetch<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    const { setTokens } = await import('../api/client')
    setTokens(data.access_token, data.refresh_token)
    await fetchUser()
  }

  const register = async (formData: { org_name: string; slug: string; email: string; password: string; name: string }) => {
    const data = await apiFetch<{ access_token: string; refresh_token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(formData),
    })
    const { setTokens } = await import('../api/client')
    setTokens(data.access_token, data.refresh_token)
    await fetchUser()
  }

  const logout = async () => {
    const { clearTokens } = await import('../api/client')
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
