import { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Projects Chart Component
export const ProjectsChart = () => {
  const data = {
    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
    datasets: [
      {
        label: 'Новые проекты',
        data: [2, 4, 3, 5, 7, 3, 4],
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#667eea',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: 'Завершенные',
        data: [1, 2, 2, 3, 4, 2, 3],
        borderColor: '#56ab2f',
        backgroundColor: 'rgba(86, 171, 47, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#56ab2f',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            family: 'Manrope',
            size: 12,
            weight: '600',
          },
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          family: 'Manrope',
          size: 13,
          weight: '600',
        },
        bodyFont: {
          family: 'Manrope',
          size: 12,
        },
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        displayColors: true,
        boxPadding: 6,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          font: {
            family: 'Manrope',
            size: 11,
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            family: 'Manrope',
            size: 11,
          },
        },
      },
    },
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Активность по проектам</h3>
      <div className="h-[300px]">
        <Line data={data} options={options} />
      </div>
    </div>
  )
}

// Status Chart Component
interface StatusChartProps {
  statusData?: {
    new: number
    in_progress: number
    completed: number
    cancelled: number
  }
}

export const StatusChart = ({ statusData }: StatusChartProps) => {
  const defaultData = statusData || {
    new: 5,
    in_progress: 12,
    completed: 8,
    cancelled: 2,
  }

  const data = {
    labels: ['Новые', 'В работе', 'Завершены', 'Отменены'],
    datasets: [
      {
        data: [
          defaultData.new,
          defaultData.in_progress,
          defaultData.completed,
          defaultData.cancelled,
        ],
        backgroundColor: ['#17a2b8', '#007bff', '#28a745', '#dc3545'],
        borderWidth: 0,
        hoverOffset: 10,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          font: {
            family: 'Manrope',
            size: 12,
            weight: '600',
          },
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          family: 'Manrope',
          size: 13,
          weight: '600',
        },
        bodyFont: {
          family: 'Manrope',
          size: 12,
        },
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
      },
    },
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Статусы проектов</h3>
      <div className="h-[300px]">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  )
}
