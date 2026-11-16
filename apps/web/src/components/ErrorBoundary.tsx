import { Component, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

/**
 * Last-resort boundary: renders a plain, honest message instead of a blank
 * page when rendering itself throws. Uses component state (not hooks) —
 * boundaries cannot be function components.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  override componentDidCatch(): void {
    // Rendering errors surface here; the console already has the stack, and
    // the boundary's job is purely the fallback UI.
  }

  override render(): ReactNode {
    if (this.state.error !== null) {
      return (
        <div role="alert" className="p-10 text-center text-sm text-slate-300">
          <p className="font-medium text-red-300">The screen failed to render.</p>
          <p className="mt-2 text-slate-400">Reload the page to continue.</p>
        </div>
      )
    }
    return this.props.children
  }
}
