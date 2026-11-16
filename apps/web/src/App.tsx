import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import { AppRoutes } from '@/app/router'
import { ErrorBoundary } from '@/components/ErrorBoundary'

/**
 * App root: query provider, crash boundary, route table. The query client
 * is created per mount (not module scope) so tests can render App without
 * shared cache leaking between cases.
 */
export default function App() {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: 1, refetchOnWindowFocus: false },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <AppRoutes />
      </ErrorBoundary>
    </QueryClientProvider>
  )
}
