import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { Truck } from 'lucide-react'

export default function DashboardLogistics() {
  const { api } = useAuth()
  const [data, setData] = useState({ items: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/logistics')
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then(setData)
      .catch(() => setData({ items: [] }))
      .finally(() => setLoading(false))
  }, [])

  const cols = data.items[0] ? Object.keys(data.items[0]) : []

  return (
    <DashboardPage
      title="Логистика"
      description="Приход, расход и остатки по складам. Данные из Анализ 2 / Логистика.xlsx."
      templateType="dashboard_logistics"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="mb-4 flex items-center gap-2 text-slate-400">
            <Truck className="w-5 h-5" />
            <span>Записей: {data.items.length}</span>
          </div>
          <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/50">
                <tr>
                  {cols.map((k) => (
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
