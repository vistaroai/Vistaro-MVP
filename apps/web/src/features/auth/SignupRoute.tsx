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
import { postSignup } from '@/features/auth/api'

const signupSchema = z.object({
  email: z.email('Enter a valid email address'),
  // Same rules as the API's SignupRequest (min 10, no control characters).
  // Written as code-point checks rather than a control-character regex so the
  // `no-control-regex` ESLint rule stays clean; intent is identical.
  password: z
    .string()
    .min(10, 'Use at least 10 characters')
    .refine(
      (value) =>
        ![...value].some((character) => {
          const code = character.codePointAt(0) ?? 0
          return code === 0 || code === 10 || code === 13
        }),
      { message: 'No control characters or line breaks' },
    ),
})

type SignupValues = z.infer<typeof signupSchema>

export function SignupRoute() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: '', password: '' },
  })

  const signup = useMutation({
    mutationFn: async (values: SignupValues) => {
      await refreshCsrfToken(api)
      return postSignup(values)
    },
    onSuccess: (_data, variables) => {
      // Session exists but is unverified: go to the "check your inbox"
      // screen. We do NOT treat the session as usable (see backend rules).
      void navigate('/verify-email', { state: { email: variables.email } })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
    },
  })

  const submitError = signup.isError ? describeError(signup.error) : null

  return (
    <AuthCard
      title="Create your Vistaro account"
      footer={
        <>
          Already have an account?{' '}
          <Link className="text-sky-300 underline-offset-4 hover:underline" to="/login">
            Sign in
          </Link>
        </>
      }
    >
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          void form.handleSubmit((values) => signup.mutate(values))(event)
        }}
      >
        {submitError ? (
          <Alert variant="destructive">
            <AlertTitle>Sign-up failed</AlertTitle>
            <AlertDescription>{submitError}</AlertDescription>
          </Alert>
        ) : null}

        <div className="flex flex-col gap-2">
          <Label htmlFor="signup-email">Email</Label>
          <Input
            id="signup-email"
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
          <Label htmlFor="signup-password">Password</Label>
          <Input
            id="signup-password"
            type="password"
            autoComplete="new-password"
            aria-invalid={form.formState.errors.password !== undefined}
            aria-describedby="signup-password-hint"
            {...form.register('password')}
          />
          <p id="signup-password-hint" className="text-xs text-slate-500">
            At least 10 characters.
          </p>
          {form.formState.errors.password ? (
            <p className="text-sm text-red-300">{form.formState.errors.password.message}</p>
          ) : null}
        </div>

        <Button type="submit" disabled={signup.isPending}>
          {signup.isPending ? 'Creating account…' : 'Create account'}
        </Button>
      </form>
    </AuthCard>
  )
}
