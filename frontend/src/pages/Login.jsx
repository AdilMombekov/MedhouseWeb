import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, user } = useAuth()
  const navigate = useNavigate()

  if (user) return <Navigate to="/" replace />

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Ошибка входа')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-slate-900 border border-slate-800 p-8 shadow-xl">
        <h1 className="text-xl font-bold text-brand-400 mb-1">Вход в систему</h1>
        <p className="text-slate-500 text-sm mb-6">Medhouse / Swiss Energy</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-slate-100 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-slate-100 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none"
              required
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium py-2.5 transition-colors disabled:opacity-50"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  )
}
