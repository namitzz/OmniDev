import { useState } from 'react'
import toast from 'react-hot-toast'

interface CreateTaskModalProps {
  onClose: () => void
  onCreate: (issueNumber: number) => Promise<void>
}

export default function CreateTaskModal({ onClose, onCreate }: CreateTaskModalProps) {
  const [issueNumber, setIssueNumber] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const num = parseInt(issueNumber)
    if (isNaN(num) || num <= 0) {
      toast.error('Please enter a valid issue number')
      return
    }

    setLoading(true)
    try {
      await onCreate(num)
      toast.success('Task created successfully')
      onClose()
    } catch (error) {
      toast.error('Failed to create task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Create New Task
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="issueNumber"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
            >
              GitHub Issue Number
            </label>
            <input
              type="number"
              id="issueNumber"
              value={issueNumber}
              onChange={(e) => setIssueNumber(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="e.g., 42"
              required
              autoFocus
            />
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              Enter the GitHub issue number to create a development task
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 btn-primary"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
              ) : (
                'Create Task'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
