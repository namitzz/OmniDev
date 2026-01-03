import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

const API_URL = process.env.API_URL || 'http://localhost:8000'

interface Task {
  id: string
  title: string
  status: string
  created_at: string
  issue_number: number
}

interface TaskListProps {
  tasks: Task[]
  onRefresh: () => void
}

export default function TaskList({ tasks, onRefresh }: TaskListProps) {
  const [selectedTask, setSelectedTask] = useState<string | null>(null)

  const getStatusClass = (status: string) => {
    const baseClass = 'status-badge '
    switch (status.toLowerCase()) {
      case 'pending':
        return baseClass + 'status-pending'
      case 'in_progress':
        return baseClass + 'status-in_progress'
      case 'completed':
        return baseClass + 'status-completed'
      case 'failed':
        return baseClass + 'status-failed'
      default:
        return baseClass + 'bg-slate-100 text-slate-800'
    }
  }

  const handleRetry = async (taskId: string) => {
    try {
      await axios.post(`${API_URL}/tasks/${taskId}/retry`)
      toast.success('Task retry initiated')
      onRefresh()
    } catch (error) {
      toast.error('Failed to retry task')
    }
  }

  const handleCancel = async (taskId: string) => {
    try {
      await axios.post(`${API_URL}/tasks/${taskId}/cancel`)
      toast.success('Task cancelled')
      onRefresh()
    } catch (error) {
      toast.error('Failed to cancel task')
    }
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-lg shadow">
        <div className="text-6xl mb-4">📋</div>
        <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
          No tasks yet
        </h3>
        <p className="text-slate-600 dark:text-slate-400">
          Create a task from a GitHub issue to get started
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="task-card cursor-pointer"
          onClick={() => setSelectedTask(task.id === selectedTask ? null : task.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  {task.title}
                </h3>
                <span className={getStatusClass(task.status)}>
                  {task.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Issue #{task.issue_number} • Created {new Date(task.created_at).toLocaleString()}
              </p>
            </div>
            <div className="flex space-x-2">
              {task.status === 'failed' && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRetry(task.id)
                  }}
                  className="btn-secondary text-sm py-1 px-3"
                >
                  Retry
                </button>
              )}
              {task.status === 'in_progress' && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleCancel(task.id)
                  }}
                  className="btn-secondary text-sm py-1 px-3"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {selectedTask === task.id && (
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <div className="text-sm text-slate-600 dark:text-slate-400">
                <p className="mb-2">
                  <strong>Task ID:</strong> {task.id}
                </p>
                <p>
                  <strong>Status:</strong> {task.status}
                </p>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
