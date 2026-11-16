import { Route, Routes } from 'react-router-dom'

import { RequireAuth } from '@/lib/auth/session'
import { AppLayout } from '@/app/layout'
import { LoginRoute } from '@/features/auth/LoginRoute'
import { SignupRoute } from '@/features/auth/SignupRoute'
import { VerifyEmailRoute } from '@/features/auth/VerifyEmailRoute'
import { DashboardRoute } from '@/routes/DashboardRoute'
import { NotFoundRoute } from '@/routes/NotFoundRoute'

/**
 * Route table. Everything inside the layout block is behind the session
 * guard: signed-out visitors bounce to /login (history-replaced), and the
 * catch-all inside the guard renders the 404 state.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route path="/signup" element={<SignupRoute />} />
      <Route path="/verify-email" element={<VerifyEmailRoute />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardRoute />} />
        <Route path="*" element={<NotFoundRoute />} />
      </Route>
    </Routes>
  )
}
