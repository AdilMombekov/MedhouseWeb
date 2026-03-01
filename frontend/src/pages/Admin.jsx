import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { UserPlus, Shield } from 'lucide-react'

export default function Admin() {
  const { api, isAdmin } = useAuth()
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('operator')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    api('/users')
      .then((r) => (r.ok ? r.json() : []))
      .then(setUsers)
      .catch(() => setUsers([]))
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage({ type: '', text: '' })
    try {
      const r = await api('/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName || null, role }),
      })
      if (r.ok) {
        const u = await r.json()
        setUsers((prev) => [u, ...prev])
        setMessage({ type: 'success', text: 'Пользователь создан' })
        setEmail('')
        setPassword('')
        setFullName('')
        setRole('operator')
      } else {
        const err = await r.json().catch(() => ({}))
        setMessage({ type: 'error', text: err.detail || 'Ошибка' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Ошибка сети' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 md:p-8">
      <h1 className="text-2xl font-bold text-slate-100 mb-2">Администрирование</h1>
      <p className="text-slate-500 mb-8">Управление пользователями: администраторы, модераторы, операторы.</p>

      {isAdmin && (
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-8">
          <h2 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <UserPlus className="w-5 h-5" />
            Добавить пользователя
          </h2>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Имя</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Роль</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              >
                <option value="operator">Оператор</option>
                <option value="moderator">Модератор</option>
                <option value="admin">Администратор</option>
              </select>
            </div>
            <div className="md:col-span-2">
              {message.text && (
                <p className={message.type === 'success' ? 'text-brand-400' : 'text-red-400'}>{message.text}</p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium px-4 py-2 disabled:opacity-50"
              >
                {loading ? 'Создание...' : 'Создать'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
        <h2 className="font-semibold text-slate-200 px-4 py-3 border-b border-slate-800 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Пользователи
        </h2>
        <table className="w-full">
          <thead className="bg-slate-800/50">
            <tr>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Email</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Имя</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Роль</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-slate-800">
                <td className="px-4 py-3 text-slate-200">{u.email}</td>
                <td className="px-4 py-3 text-slate-500">{u.full_name || '—'}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      u.role === 'admin'
                        ? 'bg-amber-500/20 text-amber-400'
                        : u.role === 'moderator'
                        ? 'bg-brand-500/20 text-brand-400'
                        : 'bg-slate-600 text-slate-400'
                    }`}
                  >
                    {u.role}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
