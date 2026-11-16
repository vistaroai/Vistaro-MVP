import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* The Vite dev proxy makes API calls same-origin, so a plain BrowserRouter
        with relative paths covers both dev and (later) staging same-zone setups. */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
