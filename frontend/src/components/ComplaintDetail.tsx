import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { complaintApi } from '../services/api'
import { Complaint, SimilarComplaint } from '../App'
import ComplaintResults from './ComplaintResults'
import SimilarComplaintsList from './SimilarComplaintsList'
import './ComplaintDetail.css'

export default function ComplaintDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [complaint, setComplaint] = useState<Complaint | null>(null)
  const [similarComplaints, setSimilarComplaints] = useState<SimilarComplaint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadComplaint()
    }
  }, [id])

  const loadComplaint = async () => {
    if (!id) return

    try {
      setLoading(true)
      const complaintData = await complaintApi.getComplaint(id)
      setComplaint(complaintData)

      // Load similar complaints
      try {
        const similarResponse = await complaintApi.findSimilarComplaints({
          complaint_id: id,
          top_k: 5
        })
        setSimilarComplaints(similarResponse.similar_complaints)
      } catch (err) {
        console.error('Error loading similar complaints:', err)
      }

      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load complaint')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="complaint-detail-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading complaint...</p>
        </div>
      </div>
    )
  }

  if (error || !complaint) {
    return (
      <div className="complaint-detail-container">
        <div className="error-state">
          <p>Error: {error || 'Complaint not found'}</p>
          <button onClick={() => navigate('/complaints')} className="btn-primary">
            Back to List
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="complaint-detail-container">
      <div className="detail-header">
        <button onClick={() => navigate('/complaints')} className="btn-back">
          ← Back to List
        </button>
        <h1>Complaint Details</h1>
      </div>

      <div className="detail-content">
        <ComplaintResults complaint={complaint} />

        {similarComplaints.length > 0 && (
          <SimilarComplaintsList similarComplaints={similarComplaints} />
        )}
      </div>
    </div>
  )
}
