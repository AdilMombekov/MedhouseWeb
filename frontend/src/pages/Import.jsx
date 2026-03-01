import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Upload, FileSpreadsheet } from 'lucide-react'

export default function Import() {
  const { api } = useAuth()
  const [companies, setCompanies] = useState([])
  const [uploads, setUploads] = useState([])
  const [file, setFile] = useState(null)
  const [reportType, setReportType] = useState('')
  const [companyId, setCompanyId] = useState('')
  const [period, setPeriod] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    api('/companies').then((r) => r.json().then(setCompanies).catch(() => setCompanies([])))
    api('/uploads').then((r) => r.json().then(setUploads).catch(() => setUploads([])))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setMessage({ type: 'error', text: 'Выберите файл' })
      return
    }
    setLoading(true)
    setMessage({ type: '', text: '' })
    const form = new FormData()
    form.append('file', file)
    if (reportType) form.append('report_type', reportType)
    if (companyId) form.append('company_id', companyId)
    if (period) form.append('period', period)
    if (notes) form.append('notes', notes)
    try {
      const r = await api('/uploads/', {
        method: 'POST',
        body: form,
        headers: {},
      })
      if (r.ok) {
        const data = await r.json()
        setUploads((prev) => [data, ...prev])
        setMessage({ type: 'success', text: 'Файл успешно загружен' })
        setFile(null)
        setReportType('')
        setPeriod('')
        setNotes('')
      } else {
        const err = await r.json().catch(() => ({}))
        setMessage({ type: 'error', text: err.detail || 'Ошибка загрузки' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Ошибка сети' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 md:p-8">
      <h1 className="text-2xl font-bold text-slate-100 mb-2">Импорт отчётов</h1>
      <p className="text-slate-500 mb-8">
        Загрузите отчёты, подготовленные в 1С по шаблону. Допустимы форматы XLSX, XLS, CSV.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-6">
          <h2 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Загрузить файл
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Файл</label>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setFile(e.target.files?.[0])}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-300 text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-brand-600 file:text-white file:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Тип отчёта</label>
              <input
                type="text"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                placeholder="Например: sales_monthly"
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Компания</label>
              <select
                value={companyId}
                onChange={(e) => setCompanyId(e.target.value)}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              >
                <option value="">— Выберите —</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Период</label>
              <input
                type="text"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                placeholder="2026-01 или 2026-Q1"
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Примечание</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
              />
            </div>
            {message.text && (
              <p className={message.type === 'success' ? 'text-brand-400' : 'text-red-400'}>{message.text}</p>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium py-2.5 disabled:opacity-50"
            >
              {loading ? 'Загрузка...' : 'Загрузить'}
            </button>
          </form>
        </div>

        <div className="rounded-xl bg-slate-900 border border-slate-800 p-6">
          <h2 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5" />
            Загруженные отчёты
          </h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {uploads.length === 0 ? (
              <p className="text-slate-500 text-sm">Пока нет загруженных файлов.</p>
            ) : (
              uploads.map((u) => (
                <div
                  key={u.id}
                  className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-800/50 border border-slate-700/50"
                >
                  <div>
                    <p className="text-slate-200 font-medium truncate max-w-[200px]">{u.file_name}</p>
                    <p className="text-xs text-slate-500">
                      {u.period && `${u.period} · `}
                      {new Date(u.created_at).toLocaleString('ru')}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
