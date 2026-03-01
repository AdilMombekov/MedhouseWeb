import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { MapPin } from 'lucide-react'

export default function DashboardRegions() {
  const { api } = useAuth()
  const [data, setData] = useState({ regions: [], total: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/dashboard/regions')
      .then((r) => (r.ok ? r.json() : { regions: [], total: 0 }))
      .then(setData)
      .catch(() => setData({ regions: [], total: 0 }))
      .finally(() => setLoading(false))
  }, [])

  return (
    <DashboardPage
      title="Регионы и филиалы"
      description="Показатели по регионам (KATO). Медхаус — 15 городов и регионов."
      templateType="dashboard_regions"
    >
      {loading ? (
        <p className="text-slate-500">Загрузка...</p>
      ) : (
        <>
          <div className="mb-4 flex items-center gap-2 text-slate-400">
            <MapPin className="w-5 h-5" />
            <span>Всего записей: {data.total}</span>
          </div>
          <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="text-left px-4 py-3 text-slate-400 font-medium">Код</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-medium">Наименование</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-medium">parent_id</th>
                </tr>
              </thead>
              <tbody>
                {data.regions.map((r) => (
                  <tr key={r.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                    <td className="px-4 py-2 text-slate-300 font-mono text-xs">{r.code}</td>
                    <td className="px-4 py-2 text-slate-200">{r.name}</td>
                    <td className="px-4 py-2 text-slate-500">{r.parent_id}</td>
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
