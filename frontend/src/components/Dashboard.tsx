import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { complaintApi } from '../services/api'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './Dashboard.css'

interface Stats {
  total_complaints: number
  total_products: number
  total_companies: number
  complaints_by_product: Record<string, number>
  complaints_by_state: Record<string, number>
}

const COLORS = ['#dbd0c0', '#c9bfb0', '#b8aea0', '#a79d90', '#968c80', '#857b70', '#746a60', '#635950']

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await complaintApi.getStats()
      setStats(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  const productData = stats
    ? Object.entries(stats.complaints_by_product)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    : []

  const stateData = stats
    ? Object.entries(stats.complaints_by_state)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
    : []

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-error">
          <p>Error: {error}</p>
          <button onClick={loadStats} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <p className="dashboard-subtitle">System-wide complaint statistics and insights</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Complaints</div>
          <div className="stat-value">{stats?.total_complaints || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Products</div>
          <div className="stat-value">{stats?.total_products || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Companies</div>
          <div className="stat-value">{stats?.total_companies || 0}</div>
        </div>
        <div className="stat-card clickable" onClick={() => navigate('/complaints')}>
          <div className="stat-label">View All</div>
          <div className="stat-value">→</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>Complaints by Product</h2>
          {productData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={productData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  stroke="var(--primary)"
                  fontSize={11}
                  tick={{ fill: 'var(--text-secondary)' }}
                />
                <YAxis 
                  stroke="var(--primary)" 
                  fontSize={11}
                  tick={{ fill: 'var(--text-secondary)' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-secondary)',
                    border: '2px solid var(--border)',
                    color: 'var(--text)',
                    borderRadius: '8px',
                    padding: '0.75rem'
                  }}
                  labelStyle={{ color: 'var(--primary)', fontWeight: 700 }}
                />
                <Bar 
                  dataKey="value" 
                  fill="var(--primary)" 
                  radius={[6, 6, 0, 0]}
                  stroke="var(--bg-secondary)"
                  strokeWidth={1}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">No data available</div>
          )}
        </div>

        <div className="chart-card">
          <h2>Complaints by State</h2>
          {stateData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={stateData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => {
                    if (percent < 0.05) return '' // Hide labels for small slices
                    return `${name}: ${(percent * 100).toFixed(0)}%`
                  }}
                  outerRadius={110}
                  fill="#8884d8"
                  dataKey="value"
                  stroke="var(--bg-secondary)"
                  strokeWidth={2}
                >
                  {stateData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-secondary)',
                    border: '2px solid var(--border)',
                    color: 'var(--text)',
                    borderRadius: '8px',
                    padding: '0.75rem'
                  }}
                  labelStyle={{ color: 'var(--primary)', fontWeight: 700 }}
                />
                <Legend
                  wrapperStyle={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">No data available</div>
          )}
        </div>
      </div>

      <div className="dashboard-actions">
        <button onClick={() => navigate('/')} className="btn-primary">
          Submit New Complaint
        </button>
        <button onClick={() => navigate('/complaints')} className="btn-secondary">
          Browse All Complaints
        </button>
      </div>
    </div>
  )
}
