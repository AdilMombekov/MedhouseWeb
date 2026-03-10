import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { API_BASE } from '../config'
import { Download } from 'lucide-react'

export default function Templates() {
  const { api } = useAuth()
  const [templates, setTemplates] = useState([])

  useEffect(() => {
    api('/templates').then((r) => r.json().then(setTemplates).catch(() => setTemplates([])))
  }, [])

  const download = (id, fileName) => {
    window.open(`${API_BASE}/api/templates/download/${id}`, '_blank')
  }

  return (
    <div className="p-6 md:p-8">
      <h1 className="text-2xl font-bold text-slate-100 mb-2">Шаблоны для отчётности</h1>
      <p className="text-slate-500 mb-8">
        Скачайте шаблон, заполните в 1С по инструкции и загрузите готовый отчёт в раздел «Импорт отчётов».
      </p>

      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-800/50">
            <tr>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Название</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Описание</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Тип</th>
              <th className="w-32 px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {templates.map((t) => (
              <tr key={t.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                <td className="px-4 py-3 text-slate-200">{t.name}</td>
                <td className="px-4 py-3 text-slate-500 text-sm">{t.description || '—'}</td>
                <td className="px-4 py-3 text-slate-500 text-sm">{t.report_type || '—'}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => download(t.id, t.file_name)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Скачать
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {templates.length === 0 && (
          <div className="px-4 py-8 text-center text-slate-500">Шаблоны пока не добавлены.</div>
        )}
      </div>
    </div>
  )
}
