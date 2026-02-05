import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { complaintApi } from '../services/api'
import { Complaint } from '../App'
import './ComplaintsList.css'

export default function ComplaintsList() {
  const [complaints, setComplaints] = useState<Complaint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    product: '',
    sub_product: '',
    company: ''
  })
  const navigate = useNavigate()

  const limit = 20

  useEffect(() => {
    loadComplaints()
  }, [page, filters])

  const loadComplaints = async () => {
    try {
      setLoading(true)
      const skip = (page - 1) * limit
      const data = await complaintApi.listComplaints({
        skip,
        limit,
        ...filters
      })
      setComplaints(data)
      // Estimate total pages (in real app, API would return total count)
      setTotalPages(Math.max(1, Math.ceil(data.length / limit)))
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1) // Reset to first page on filter change
  }

  const handleComplaintClick = (complaintId: string) => {
    navigate(`/complaints/${complaintId}`)
  }

  if (loading && complaints.length === 0) {
    return (
      <div className="complaints-list-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading complaints...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="complaints-list-container">
      <div className="list-header">
        <h1>Browse Complaints</h1>
        <p className="list-subtitle">View and search through all submitted complaints</p>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label>Product</label>
          <input
            type="text"
            value={filters.product}
            onChange={(e) => handleFilterChange('product', e.target.value)}
            placeholder="Filter by product..."
          />
        </div>
        <div className="filter-group">
          <label>Sub-Product</label>
          <input
            type="text"
            value={filters.sub_product}
            onChange={(e) => handleFilterChange('sub_product', e.target.value)}
            placeholder="Filter by sub-product..."
          />
        </div>
        <div className="filter-group">
          <label>Company</label>
          <input
            type="text"
            value={filters.company}
            onChange={(e) => handleFilterChange('company', e.target.value)}
            placeholder="Filter by company..."
          />
        </div>
        <button
          onClick={() => {
            setFilters({ product: '', sub_product: '', company: '' })
            setPage(1)
          }}
          className="btn-clear-filters"
        >
          Clear Filters
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠</span>
          {error}
        </div>
      )}

      <div className="complaints-grid">
        {complaints.map((complaint) => (
          <div
            key={complaint.id}
            className="complaint-card"
            onClick={() => handleComplaintClick(complaint.complaint_id)}
          >
            <div className="card-header-row">
              <div className="complaint-id-small">#{complaint.complaint_id.slice(0, 8)}</div>
              {complaint.product && (
                <span className="product-badge">{complaint.product}</span>
              )}
            </div>
            <div className="complaint-preview-text">
              {complaint.complaint_text.length > 150
                ? `${complaint.complaint_text.substring(0, 150)}...`
                : complaint.complaint_text}
            </div>
            {complaint.summary && (
              <div className="complaint-summary-small">
                {complaint.summary}
              </div>
            )}
            <div className="card-footer-row">
              {complaint.company && (
                <span className="meta-info">{complaint.company}</span>
              )}
              {complaint.state && (
                <span className="meta-info">{complaint.state}</span>
              )}
              <span className="meta-info">
                {new Date(complaint.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>

      {complaints.length === 0 && !loading && (
        <div className="empty-state">
          <p>No complaints found</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Submit First Complaint
          </button>
        </div>
      )}

      {complaints.length > 0 && (
        <div className="pagination">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-pagination"
          >
            ← Previous
          </button>
          <span className="page-info">
            Page {page} {totalPages > 1 && `of ${totalPages}`}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={complaints.length < limit}
            className="btn-pagination"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
