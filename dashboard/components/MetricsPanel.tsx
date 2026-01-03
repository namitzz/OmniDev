interface MetricsPanelProps {
  metrics: {
    total_tasks: number
    completed_tasks: number
    failed_tasks: number
    total_cost: number
    total_tokens: number
  }
}

export default function MetricsPanel({ metrics }: MetricsPanelProps) {
  const successRate = metrics.total_tasks > 0
    ? ((metrics.completed_tasks / metrics.total_tasks) * 100).toFixed(1)
    : '0.0'

  const cards = [
    {
      title: 'Total Tasks',
      value: metrics.total_tasks,
      icon: '📊',
      color: 'bg-blue-50 dark:bg-blue-900/20'
    },
    {
      title: 'Completed',
      value: metrics.completed_tasks,
      icon: '✅',
      color: 'bg-green-50 dark:bg-green-900/20'
    },
    {
      title: 'Failed',
      value: metrics.failed_tasks,
      icon: '❌',
      color: 'bg-red-50 dark:bg-red-900/20'
    },
    {
      title: 'Success Rate',
      value: `${successRate}%`,
      icon: '📈',
      color: 'bg-purple-50 dark:bg-purple-900/20'
    },
    {
      title: 'Total Cost',
      value: `$${metrics.total_cost.toFixed(2)}`,
      icon: '💰',
      color: 'bg-yellow-50 dark:bg-yellow-900/20'
    },
    {
      title: 'Tokens Used',
      value: metrics.total_tokens.toLocaleString(),
      icon: '🔢',
      color: 'bg-indigo-50 dark:bg-indigo-900/20'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.color} rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                {card.title}
              </p>
              <p className="mt-2 text-3xl font-semibold text-slate-900 dark:text-white">
                {card.value}
              </p>
            </div>
            <div className="text-4xl">{card.icon}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
