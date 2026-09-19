import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/new', label: 'New Interview', icon: '🎯' },
  { to: '/sessions', label: 'Past Sessions', icon: '🗂️' },
]

export default function DashboardLayout() {
  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="px-6 py-5 border-b border-slate-200">
          <h1 className="text-lg font-bold text-slate-800">AI Interview</h1>
          <p className="text-xs text-slate-400 mt-0.5">Candidate Screening System</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-4 border-t border-slate-200 text-xs text-slate-400">
          RAG-powered · Role-grounded questions
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 bg-white border-b border-slate-200 flex items-center px-6">
          <span className="text-sm text-slate-500">Technical Screening Dashboard</span>
        </header>
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
