function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-400">Vistaro</p>
        <h1 className="mt-4 text-5xl font-semibold tracking-tight">Bootstrap shell</h1>
        <p className="mt-6 max-w-xl text-lg text-slate-300">
          The API and web foundation are running. Product modules arrive in later tasks.
        </p>
        <div className="mt-10 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-sm text-slate-400">API health</p>
          <a
            className="mt-2 inline-block font-mono text-sky-300 hover:text-sky-200"
            href="http://127.0.0.1:8000/healthz"
          >
            http://127.0.0.1:8000/healthz
          </a>
        </div>
      </div>
    </main>
  )
}

export default App
