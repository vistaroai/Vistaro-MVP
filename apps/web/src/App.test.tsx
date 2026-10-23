import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders the bootstrap heading', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: /bootstrap shell/i })).toBeInTheDocument()
  })
})
