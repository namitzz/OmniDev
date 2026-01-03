import Head from 'next/head'
import { useState, useEffect } from 'react'
import axios from 'axios'
import TaskList from '../components/TaskList'
import MetricsPanel from '../components/MetricsPanel'
import CreateTaskModal from '../components/CreateTaskModal'
import Navbar from '../components/Navbar'

const API_URL = process.env.API_URL || 'http://localhost:8000'

interface Task {
  id: string
  title: string
  status: string
  created_at: string
  issue_number: number
}

interface Metrics {
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  total_cost: number
  total_tokens: number
}

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    fetchData()
    // Poll every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [tasksRes, metricsRes] = await Promise.all([
        axios.get(`${API_URL}/tasks`),
        axios.get(`${API_URL}/metrics`)
      ])
      setTasks(tasksRes.data.tasks || [])
      setMetrics(metricsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async (issueNumber: number) => {
    try {
      await axios.post(`${API_URL}/tasks`, { issue_number: issueNumber })
      setShowCreateModal(false)
      fetchData()
    } catch (error) {
      console.error('Failed to create task:', error)
      alert('Failed to create task')
    }
  }

  return (
    <>
      <Head>
        <title>DevHive - AI Development Team Dashboard</title>
        <meta name="description" content="Autonomous AI development team dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <Navbar onCreateTask={() => setShowCreateModal(true)} />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Metrics Panel */}
          {metrics && <MetricsPanel metrics={metrics} />}

          {/* Task List */}
          <div className="mt-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Active Tasks
              </h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary"
              >
                + New Task
              </button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                <p className="mt-4 text-slate-600 dark:text-slate-400">Loading tasks...</p>
              </div>
            ) : (
              <TaskList tasks={tasks} onRefresh={fetchData} />
            )}
          </div>
        </main>

        {/* Create Task Modal */}
        {showCreateModal && (
          <CreateTaskModal
            onClose={() => setShowCreateModal(false)}
            onCreate={handleCreateTask}
          />
        )}
      </div>
    </>
  )
}
