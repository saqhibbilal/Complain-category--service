import { useState } from 'react'
import { complaintApi, ComplaintCreateRequest } from '../services/api'
import { Complaint, SimilarComplaint } from '../App'
import './ComplaintSubmissionForm.css'

interface Props {
  onSubmitted: (complaint: Complaint, similar: SimilarComplaint[]) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function ComplaintSubmissionForm({ onSubmitted, isLoading, setIsLoading }: Props) {
  const [complaintText, setComplaintText] = useState('')
  const [company, setCompany] = useState('')
  const [state, setState] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!complaintText.trim()) {
      setError('Please enter a complaint description')
      return
    }

    if (complaintText.trim().length < 10) {
      setError('Complaint must be at least 10 characters long')
      return
    }

    setIsLoading(true)

    try {
      // Submit complaint
      const complaintData: ComplaintCreateRequest = {
        complaint_text: complaintText,
        company: company || undefined,
        state: state || undefined,
      }

      const complaint = await complaintApi.createComplaint(complaintData)

      // Find similar complaints
      const similarResponse = await complaintApi.findSimilarComplaints({
        complaint_id: complaint.complaint_id,
        top_k: 5,
      })

      onSubmitted(complaint, similarResponse.similar_complaints)
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to submit complaint. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="complaint-form-container">
      <div className="form-card">
        <h2>Submit a Complaint</h2>
        <p className="form-description">
          Enter your complaint details below. Our AI system will categorize it and find similar complaints.
        </p>

        <form onSubmit={handleSubmit} className="complaint-form">
          <div className="form-group">
            <label htmlFor="complaint-text">
              Complaint Description <span className="required">*</span>
            </label>
            <textarea
              id="complaint-text"
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              placeholder="Describe your complaint in detail..."
              rows={8}
              required
              disabled={isLoading}
              className={error && !complaintText.trim() ? 'error' : ''}
            />
            <div className="char-count">
              {complaintText.length} characters
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="company">Company (Optional)</label>
              <input
                id="company"
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Company name"
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="state">State (Optional)</label>
              <input
                id="state"
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="State code (e.g., NY)"
                maxLength={2}
                disabled={isLoading}
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !complaintText.trim()}
          >
            {isLoading ? 'Processing...' : 'Submit Complaint'}
          </button>
        </form>
      </div>
    </div>
  )
}
