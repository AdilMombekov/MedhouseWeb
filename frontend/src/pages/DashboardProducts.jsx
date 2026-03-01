import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Package } from 'lucide-react'

export default function DashboardProducts() {
  const { api } = useAuth()
  const [data, setData] = useState({ year: '2024', items: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/products')
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then(setData)
      .catch(() => setData({ year: '2024', items: [] }))
      .finally(() => setLoading(false))
  }, [])

  const chartData = data.items.slice(0, 15).map((item, i) => {
    const keys = Object.keys(item)
    const name = item.Наименование || (keys[0] ? item[keys[0]] : null) || 'Товар ' + (i + 1)
    const val = Number(item.Сумма ?? item['Кол-во'] ?? 0) || 0
    return { name: String(name).slice(0, 20), value: val }
  })

  return (
    <DashboardPage
      title="Товарная номенклатура"
      description="Продажи по товарам и группам. Парафармация, данные из Анализ 2."
      templateType="dashboard_products"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="mb-4 flex items-center gap-2 text-slate-400">
            <Package className="w-5 h-5" />
            <span>Год: {data.year}. Показано до 15 позиций.</span>
          </div>
          {chartData.length > 0 && (
            <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-6">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 100 }}>
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis type="category" dataKey="name" stroke="#64748b" width={95} tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                  <Bar dataKey="value" fill="#319765" radius={[0, 4, 4, 0]} />
                </BarChart>
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
                {data.items.slice(0, 25).map((row, i) => (
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
