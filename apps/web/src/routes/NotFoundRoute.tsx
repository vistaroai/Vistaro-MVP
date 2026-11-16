import { Link } from 'react-router-dom'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export function NotFoundRoute() {
  return (
    <main className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <Alert className="max-w-md">
        <AlertTitle>Page not found</AlertTitle>
        <AlertDescription>
          The page you tried to open doesn’t exist.{' '}
          <Link className="text-sky-300 underline-offset-4 hover:underline" to="/">
            Back to your workspace
          </Link>
        </AlertDescription>
      </Alert>
    </main>
  )
}
