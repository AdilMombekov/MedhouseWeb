import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Briefcase } from 'lucide-react'

export default function DashboardExecutive() {
  const { api } = useAuth()
  const [data, setData] = useState({ summary: { years: [], total_value: [] }, companies: [], description: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/executive')
      .then((r) => (r.ok ? r.json() : {}))
      .then(setData)
      .catch(() => setData({ summary: { years: [], total_value: [] }, companies: [], description: '' }))
      .finally(() => setLoading(false))
  }, [])

  const chartData = (data.summary?.years || []).map((y, i) => ({
    year: y,
    value: data.summary?.total_value?.[i] ?? 0,
  }))

  return (
    <DashboardPage
      title="Отчёт для руководства"
      description="Сводные ключевые показатели по годам для принятия решений."
      templateType="dashboard_executive"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="mb-6 flex items-center gap-2 text-slate-400">
            <Briefcase className="w-5 h-5" />
            <span>{data.description}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {data.companies?.map((c) => (
              <div key={c} className="rounded-xl bg-slate-900 border border-slate-800 p-5">
                <h3 className="font-semibold text-slate-200">{c}</h3>
                <p className="text-sm text-slate-500 mt-1">Консолидированные данные по компании</p>
              </div>
            ))}
          </div>
          {chartData.length > 0 && (
            <div className="rounded-xl bg-slate-900 border border-slate-800 p-6">
              <h3 className="text-slate-200 font-medium mb-4">Динамика по годам</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <XAxis dataKey="year" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => (v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `${(v / 1e3).toFixed(0)}K` : v)} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                  <Bar dataKey="value" fill="#319765" radius={[4, 4, 0, 0]} name="Показатель" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </DashboardPage>
  )
}
