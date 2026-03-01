import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = 'medhouse_token'
const API = '/api'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setTokenState] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [loading, setLoading] = useState(true)

  const setToken = useCallback((t) => {
    if (t) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.removeItem(TOKEN_KEY)
    setTokenState(t)
  }, [])

  const fetchUser = useCallback(async () => {
    const t = localStorage.getItem(TOKEN_KEY)
    if (!t) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const r = await fetch(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
      })
      if (r.ok) {
        const u = await r.json()
        setUser(u)
      } else {
        setToken(null)
        setUser(null)
      }
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [setToken])

  useEffect(() => {
    fetchUser()
  }, [token, fetchUser])

  const login = useCallback(async (email, password) => {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    const r = await fetch(`${API}/auth/login`, {
      method: 'POST',
      body: form,
    })
    if (!r.ok) {
      const e = await r.json().catch(() => ({}))
      throw new Error(e.detail || 'Ошибка входа')
    }
    const data = await r.json()
    setToken(data.access_token)
    setUser(data.user)
    return data
  }, [setToken])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [setToken])

  const isAdmin = user?.role === 'admin'
  const isModerator = user?.role === 'moderator' || user?.role === 'admin'

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        fetchUser,
        setToken,
        isAdmin,
        isModerator,
        api: (path, opts = {}) =>
          fetch(`${API}${path}`, {
            ...opts,
            headers: {
              Authorization: token ? `Bearer ${token}` : '',
              ...opts.headers,
            },
          }),
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
