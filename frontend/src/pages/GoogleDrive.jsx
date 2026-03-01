import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Cloud, CheckCircle, XCircle, FileText } from 'lucide-react'

export default function GoogleDrive() {
  const { api } = useAuth()
  const [status, setStatus] = useState(null)
  const [folderId, setFolderId] = useState('')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/google-drive/status')
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ connected: false, message: 'Ошибка запроса' }))
      .finally(() => setLoading(false))
  }, [])

  const loadFiles = () => {
    if (!folderId) return
    setLoading(true)
    api(`/google-drive/files?folder_id=${encodeURIComponent(folderId)}`)
      .then((r) => (r.ok ? r.json() : { files: [] }))
      .then((d) => setFiles(d.files || []))
      .catch(() => setFiles([]))
      .finally(() => setLoading(false))
  }

  return (
    <div className="p-6 md:p-8">
      <h1 className="text-2xl font-bold text-slate-100 mb-2">Google Drive</h1>
      <p className="text-slate-500 mb-8">
        Подключите учётную запись Google, чтобы загружать управленческую отчётность из папок и документов.
      </p>

      {loading && !status ? (
        <div className="text-slate-500">Проверка подключения...</div>
      ) : (
        <>
          <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 mb-8">
            <div className="flex items-center gap-4 mb-4">
              {status?.connected ? (
                <CheckCircle className="w-10 h-10 text-brand-500" />
              ) : (
                <XCircle className="w-10 h-10 text-amber-500" />
              )}
              <div>
                <h2 className="font-semibold text-slate-200">
                  {status?.connected ? 'Google Drive подключён' : 'Google Drive не настроен'}
                </h2>
                <p className="text-sm text-slate-500">{status?.message}</p>
              </div>
            </div>

            {!status?.connected && (
              <div className="mt-6 p-4 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-300 space-y-3">
                <p className="font-medium text-slate-200">Как подключить:</p>
                <ol className="list-decimal list-inside space-y-2">
                  <li>Создайте проект в Google Cloud Console: <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-brand-400 hover:underline">console.cloud.google.com</a>.</li>
                  <li>Включите API «Google Drive API» в разделе «API и сервисы».</li>
                  <li>Создайте учётные данные OAuth 2.0 (тип «Приложение для ПК»), скачайте файл и переименуйте в <code className="bg-slate-700 px-1 rounded">credentials.json</code>.</li>
                  <li>Положите <code className="bg-slate-700 px-1 rounded">credentials.json</code> в папку <code className="bg-slate-700 px-1 rounded">backend</code> (рядом с <code className="bg-slate-700 px-1 rounded">main.py</code>).</li>
                  <li>Перезапустите бэкенд. При первом запросе к списку файлов откроется браузер для входа в Google — войдите и разрешите доступ.</li>
                </ol>
                <p className="text-slate-500 mt-2">
                  После этого я (сервер) смогу читать файлы из вашего Google Drive по указанным вами ID папок или документов.
                </p>
              </div>
            )}

            {status?.connected && (
              <div className="mt-6">
                <label className="block text-sm text-slate-400 mb-2">ID папки на Google Drive</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={folderId}
                    onChange={(e) => setFolderId(e.target.value)}
                    placeholder="Скопируйте ID из ссылки на папку"
                    className="flex-1 rounded-lg bg-slate-800 border border-slate-700 px-4 py-2 text-slate-100"
                  />
                  <button
                    onClick={loadFiles}
                    disabled={loading}
                    className="rounded-lg bg-brand-600 hover:bg-brand-500 text-white px-4 py-2 disabled:opacity-50"
                  >
                    {loading ? 'Загрузка...' : 'Список файлов'}
                  </button>
                </div>
                {files.length > 0 && (
                  <ul className="mt-4 space-y-2">
                    {files.map((f) => (
                      <li key={f.id} className="flex items-center gap-2 py-2 px-3 rounded-lg bg-slate-800">
                        <FileText className="w-4 h-4 text-slate-500" />
                        <span className="text-slate-200 truncate flex-1">{f.name}</span>
                        <span className="text-xs text-slate-500">{f.mimeType}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
