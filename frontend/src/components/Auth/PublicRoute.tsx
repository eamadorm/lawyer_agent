
import { Navigate, Outlet } from 'react-router-dom'

export const PublicRoute = () => {
    const userId = localStorage.getItem('user_id')

    if (userId) {
        return <Navigate to="/chat" replace />
    }

    return <Outlet />
}
