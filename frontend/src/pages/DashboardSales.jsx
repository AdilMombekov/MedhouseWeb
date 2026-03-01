import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function DashboardSales() {
  const { api } = useAuth()
  const [data, setData] = useState({ year: '2024', items: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/sales')
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then(setData)
      .catch(() => setData({ year: '2024', items: [] }))
      .finally(() => setLoading(false))
  }, [])

  const chartData = data.items.slice(0, 12).map((item, i) => ({
    name: item.Период || item[Object.keys(item)[0]] || `Период ${i + 1}`,
    value: Number(item.Сумма ?? item.Количество ?? Object.values(item).find((v) => typeof v === 'number')) || 0,
  }))

  return (
    <DashboardPage
      title="Продажи"
      description="Динамика продаж по периодам и филиалам. Данные из Анализ 2."
      templateType="dashboard_sales"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
            <p className="text-slate-500 text-sm mb-4">Год: {data.year}. График по первым показателям.</p>
            {chartData.length > 0 && (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                  <Bar dataKey="value" fill="#319765" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
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
                {data.items.slice(0, 20).map((row, i) => (
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
