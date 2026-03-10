import { API_BASE } from '../config'
import { Download } from 'lucide-react'

export default function DashboardPage({ title, description, templateType, children }) {
  const downloadTemplate = () => {
    window.open(`${API_BASE}/api/templates/download-by-type/${templateType}`, '_blank')
  }

  return (
    <div className="p-6 md:p-8">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">{title}</h1>
          {description && <p className="text-slate-500 mt-1">{description}</p>}
        </div>
        <button
          onClick={downloadTemplate}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm"
        >
          <Download className="w-4 h-4" />
          Скачать шаблон выгрузки
        </button>
      </div>
      {children}
    </div>
  )
}
