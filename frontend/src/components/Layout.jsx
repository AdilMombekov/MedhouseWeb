import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Upload, FileSpreadsheet, Users, Cloud, LogOut, ShoppingCart, MapPin, Truck, Package, Target, Briefcase, Map } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const nav = [
  { to: '/', label: 'Сводка (KPI)', icon: LayoutDashboard },
  { to: '/sales', label: 'Продажи', icon: ShoppingCart },
  { to: '/regions', label: 'Регионы и филиалы', icon: MapPin },
  { to: '/map', label: 'Карта точек', icon: Map },
  { to: '/logistics', label: 'Логистика', icon: Truck },
  { to: '/products', label: 'Товарная номенклатура', icon: Package },
  { to: '/plan-fact', label: 'План–факт', icon: Target },
  { to: '/executive', label: 'Отчёт для руководства', icon: Briefcase },
  { to: '/import', label: 'Импорт отчётов', icon: Upload },
  { to: '/templates', label: 'Шаблоны', icon: FileSpreadsheet },
  { to: '/google-drive', label: 'Google Drive', icon: Cloud },
  { to: '/admin', label: 'Администрирование', icon: Users },
]

export default function Layout() {
  const { user, logout, isModerator } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h1 className="font-bold text-brand-400 text-lg">Medhouse / Swiss</h1>
          <p className="text-xs text-slate-500 mt-0.5">Управленческая отчётность</p>
        </div>
        <nav className="flex-1 p-2">
          {nav.map(({ to, label, icon: Icon }) => {
            if (to === '/admin' && !isModerator) return null
            return (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive ? 'bg-brand-600/20 text-brand-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`
                }
              >
                <Icon className="w-5 h-5 shrink-0" />
                {label}
              </NavLink>
            )
          })}
        </nav>
        <div className="p-3 border-t border-slate-800">
          <p className="text-xs text-slate-500 truncate px-2" title={user?.email}>{user?.email}</p>
          <p className="text-xs text-slate-600 capitalize px-2">{user?.role}</p>
          <button
            onClick={handleLogout}
            className="mt-2 flex items-center gap-2 w-full px-3 py-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-red-400 text-sm"
          >
            <LogOut className="w-4 h-4" />
            Выход
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
