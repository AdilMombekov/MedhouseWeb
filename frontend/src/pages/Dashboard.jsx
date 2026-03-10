import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { useAuth } from '../context/AuthContext'
import { API_BASE } from '../config'
import { TrendingUp, Building2, Package, Download } from 'lucide-react'

export default function Dashboard() {
  const { api } = useAuth()
  const [sources, setSources] = useState([])
  const [aggregate, setAggregate] = useState({ data: [], meta: {} })
  const [preview, setPreview] = useState(null)
  const [selectedSource, setSelectedSource] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const controller = new AbortController()
    const opts = { signal: controller.signal }
    const timeoutId = setTimeout(() => controller.abort(), 8000)
    api('/analytics/bootstrap', opts)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (cancelled) return
        if (data) {
          setError(null)
          setSources(Array.isArray(data.sources) ? data.sources : [])
          setAggregate(data.aggregate || { data: [], meta: {} })
        } else {
          setSources([])
          setAggregate({ data: [], meta: {} })
        }
      })
      .catch(() => {
        if (!cancelled) {
          setSources([])
          setAggregate({ data: [], meta: {} })
          setError('Не удалось загрузить данные. Проверьте, что бэкенд запущен на http://127.0.0.1:8000')
        }
      })
      .finally(() => {
        clearTimeout(timeoutId)
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
      clearTimeout(timeoutId)
      controller.abort()
    }
  }, [])

  const loadPreview = (sourceId) => {
    setSelectedSource(sourceId)
    api(`/analytics/preview?source_id=${encodeURIComponent(sourceId)}&rows=30`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setPreview)
  }

  const downloadSummaryTemplate = () => {
    window.open(`${API_BASE}/api/templates/download-by-type/dashboard_summary`, '_blank')
  }

  return (
    <div className="p-6 md:p-8">
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Сводка (KPI)</h1>
          <p className="text-slate-500 mt-1">
            Аналитика по данным <strong className="text-brand-400">Анализ 2</strong> и референсам
          </p>
          {error && (
            <p className="mt-2 text-amber-400 text-sm">{error}</p>
          )}
        </div>
        <button
          onClick={downloadSummaryTemplate}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm"
        >
          <Download className="w-4 h-4" />
          Скачать шаблон выгрузки
        </button>
      </div>

      {/* Карточки компаний */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 flex items-center justify-center">
            <Building2 className="w-6 h-6 text-brand-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-200">Медхаус</h3>
            <p className="text-sm text-slate-500">Дистрибьютор парафармации, 15 городов и регионов</p>
          </div>
        </div>
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
            <Package className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-200">Свисс Энерджи</h3>
            <p className="text-sm text-slate-500">Контролирующая компания Swiss Group, производство UA/BG/CN</p>
          </div>
        </div>
      </div>

      {/* Анализ 2 — блок с акцентом */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-brand-400 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Анализ 2 — основные показатели
        </h2>
        {loading ? (
          <div className="rounded-xl bg-slate-900 border border-slate-800 p-8 text-center text-slate-500">
            Загрузка данных...
          </div>
        ) : (
          <div className="rounded-xl bg-slate-900 border border-slate-800 p-6">
            <p className="text-slate-500 text-sm mb-4">{aggregate.meta?.description}</p>
            {aggregate.data?.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={aggregate.data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <XAxis dataKey="period" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => (v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `${(v / 1e3).toFixed(0)}K` : v)} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                      formatter={(value, name, props) => [Number(value).toLocaleString('ru'), props.payload?.rows ? `Записей: ${props.payload.rows}` : 'Значение']}
                    />
                    <Bar dataKey="value" fill="#319765" radius={[4, 4, 0, 0]} name="Показатель" />
                  </BarChart>
                </ResponsiveContainer>
                <p className="text-slate-500 text-xs mt-2">Всего периодов: {aggregate.data.length}</p>
              </>
            ) : (
              <p className="text-slate-500 py-4">Нет данных. Загрузите файлы 2020–2025.xlsx в папку «Анализ 2» в корне проекта.</p>
            )}
          </div>
        )}
      </section>

      {/* Источники Анализ 2 — выбор и превью */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Источники данных (Анализ 2)</h2>
        <div className="flex flex-wrap gap-2 mb-4">
          {sources.map((s) => (
            <button
              key={s.id}
              onClick={() => loadPreview(s.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedSource === s.id
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {s.name}
            </button>
          ))}
        </div>
        {preview && (
          <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
            <div className="px-4 py-2 border-b border-slate-800 text-sm text-slate-500">
              Превью таблицы (первые 30 строк)
            </div>
            <div className="overflow-x-auto max-h-80">
              <table className="w-full text-sm">
                <thead className="bg-slate-800/50 sticky top-0">
                  <tr>
                    {preview.columns?.map((col, i) => (
                      <th key={i} className="text-left px-3 py-2 text-slate-400 font-medium whitespace-nowrap">
                        {col || `Col ${i + 1}`}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.rows?.map((row, ri) => (
                    <tr key={ri} className="border-t border-slate-800/50 hover:bg-slate-800/30">
                      {row.map((cell, ci) => (
                        <td key={ci} className="px-3 py-2 text-slate-300 whitespace-nowrap">
                          {cell !== null && cell !== undefined ? String(cell) : ''}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
