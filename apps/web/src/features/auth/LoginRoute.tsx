import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api/client'
import { describeError } from '@/lib/api/requests'
import { refreshCsrfToken } from '@/lib/api/csrf'
import { AuthCard } from '@/features/auth/AuthCard'
import { postLogin } from '@/features/auth/api'

const loginSchema = z.object({
  email: z.email('Enter a valid email address'),
  password: z.string().min(1, 'Enter your password'),
})

type LoginValues = z.infer<typeof loginSchema>

export function LoginRoute() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const login = useMutation({
    // GET /csrf first: it re-binds the pairing cookie to whatever session is
    // still valid, so an old token from an expired session can never block
    // the login itself. The fresh login response then rewrites the cookie.
    mutationFn: async (values: LoginValues) => {
      await refreshCsrfToken(api)
      return postLogin(values)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['session'] })
      void navigate('/')
    },
  })

  const submitError = login.isError ? describeError(login.error) : null

  return (
    <AuthCard
      title="Sign in to Vistaro"
      footer={
        <>
          No account yet?{' '}
          <Link className="text-sky-300 underline-offset-4 hover:underline" to="/signup">
            Sign up
          </Link>
        </>
      }
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          void form.handleSubmit((values) => login.mutate(values))(event)
        }}
      >
        {submitError ? (
          <Alert variant="destructive">
            <AlertTitle>Sign-in failed</AlertTitle>
            <AlertDescription>{submitError}</AlertDescription>
          </Alert>
        ) : null}

        <div className="flex flex-col gap-2">
          <Label htmlFor="login-email">Email</Label>
          <Input
            id="login-email"
            autoComplete="email"
            inputMode="email"
            aria-invalid={form.formState.errors.email !== undefined}
            {...form.register('email')}
          />
          {form.formState.errors.email ? (
            <p className="text-sm text-red-300">{form.formState.errors.email.message}</p>
          ) : null}
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="login-password">Password</Label>
          <Input
            id="login-password"
            type="password"
            autoComplete="current-password"
            aria-invalid={form.formState.errors.password !== undefined}
            {...form.register('password')}
          />
          {form.formState.errors.password ? (
            <p className="text-sm text-red-300">{form.formState.errors.password.message}</p>
          ) : null}
        </div>

        <Button type="submit" disabled={login.isPending}>
          {login.isPending ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>

      <p className="text-center text-sm text-slate-400">
        or{' '}
        <a
          className="text-sky-300 underline-offset-4 hover:underline"
          href="/auth/google/login"
        >
          continue with Google
        </a>
      </p>
    </AuthCard>
  )
}
