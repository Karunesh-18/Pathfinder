import { Navigate, Outlet } from 'react-router-dom'

import { LoadingSkeleton } from '../common/LoadingSkeleton'
import { useAuth } from '../../context/AuthContext'

export function ProtectedRoute() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl py-10">
        <LoadingSkeleton lines={4} />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
