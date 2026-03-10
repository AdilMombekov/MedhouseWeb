import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import DashboardPage from '../components/DashboardPage'
import { Map } from 'lucide-react'

const DEFAULT_EMBED_URL = 'https://www.google.com/maps/d/embed?mid=1EnFUYAd5niHCSLzADwCIPyKZ7ujrJ0U'

export default function MapPage() {
  const { api } = useAuth()
  const [embedUrl, setEmbedUrl] = useState(DEFAULT_EMBED_URL)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/map/embed')
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.embedUrl) setEmbedUrl(data.embedUrl)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [api])

  return (
    <DashboardPage
      title="Карта точек"
      description="Карта филиалов и точек Медхаус (Google My Maps)."
      templateType="map"
    >
      <div className="mb-4 flex items-center gap-2 text-slate-400">
        <Map className="w-5 h-5" />
        <span>Все точки на одной карте</span>
      </div>
      <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-900" style={{ minHeight: '600px' }}>
        {loading ? (
          <div className="flex items-center justify-center h-[600px] text-slate-500">Загрузка карты...</div>
        ) : (
          <iframe
            title="Медхаус — карта точек"
            src={embedUrl}
            width="100%"
            height="600"
            style={{ border: 0 }}
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        )}
      </div>
    </DashboardPage>
  )
}
