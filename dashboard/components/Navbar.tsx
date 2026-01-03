interface NavbarProps {
  onCreateTask: () => void
}

export default function Navbar({ onCreateTask }: NavbarProps) {
  return (
    <nav className="bg-white dark:bg-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                🚀 DevHive
              </h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <a
                href="/"
                className="border-primary-500 text-slate-900 dark:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Dashboard
              </a>
              <a
                href="/agents"
                className="border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Agents
              </a>
              <a
                href="/policies"
                className="border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Policies
              </a>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={onCreateTask}
              className="btn-primary text-sm"
            >
              + New Task
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
