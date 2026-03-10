import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import DashboardSales from './pages/DashboardSales'
import DashboardRegions from './pages/DashboardRegions'
import DashboardLogistics from './pages/DashboardLogistics'
import DashboardProducts from './pages/DashboardProducts'
import DashboardPlanFact from './pages/DashboardPlanFact'
import DashboardExecutive from './pages/DashboardExecutive'
import Import from './pages/Import'
import Templates from './pages/Templates'
import Admin from './pages/Admin'
import GoogleDrive from './pages/GoogleDrive'
import Map from './pages/Map'
import { useAuth } from './context/AuthContext'

function Protected({ children, requireModerator }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="p-8 text-center">Загрузка...</div>
  if (!user) return <Navigate to="/login" replace />
  if (requireModerator && !['admin', 'moderator'].includes(user.role))
    return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="sales" element={<DashboardSales />} />
        <Route path="regions" element={<DashboardRegions />} />
        <Route path="map" element={<Map />} />
        <Route path="logistics" element={<DashboardLogistics />} />
        <Route path="products" element={<DashboardProducts />} />
        <Route path="plan-fact" element={<DashboardPlanFact />} />
        <Route path="executive" element={<DashboardExecutive />} />
        <Route path="import" element={<Protected requireModerator><Import /></Protected>} />
        <Route path="templates" element={<Templates />} />
        <Route path="google-drive" element={<GoogleDrive />} />
        <Route path="admin" element={<Protected requireModerator><Admin /></Protected>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
