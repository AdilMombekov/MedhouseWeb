import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Line, LineChart } from 'recharts'
import { Target } from 'lucide-react'

export default function DashboardPlanFact() {
  const { api } = useAuth()
  const [data, setData] = useState({ year: '2025', items: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/plan-fact')
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then(setData)
      .catch(() => setData({ year: '2025', items: [] }))
      .finally(() => setLoading(false))
  }, [])

  const chartData = data.items.map((item) => ({
    period: item.Период || item[Object.keys(item)[0]] || '',
    plan: Number(item.План ?? item.план ?? 0) || 0,
    fact: Number(item.Факт ?? item.факт ?? 0) || 0,
    pct: Number(item['Выполнение %'] ?? item['Выполнение %'] ?? 0) || 0,
  }))

  return (
    <DashboardPage
      title="План–факт"
      description="Сравнение плановых и фактических показателей по периодам."
      templateType="dashboard_plan_fact"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="mb-4 flex items-center gap-2 text-slate-400">
            <Target className="w-5 h-5" />
            <span>Год: {data.year}</span>
          </div>
          {chartData.length > 0 && (
            <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <XAxis dataKey="period" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                  <Line type="monotone" dataKey="plan" stroke="#94a3b8" name="План" strokeWidth={2} />
                  <Line type="monotone" dataKey="fact" stroke="#319765" name="Факт" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/50">
                <tr>
                  {data.items[0] && Object.keys(data.items[0]).map((k) => (
                    <th key={k} className="text-left px-4 py-3 text-slate-400 font-medium">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.items.map((row, i) => (
                  <tr key={i} className="border-t border-slate-800">
                    {Object.values(row).map((v, j) => (
                      <td key={j} className="px-4 py-2 text-slate-300">{String(v)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </DashboardPage>
  )
}
