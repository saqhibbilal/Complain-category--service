import { Complaint } from '../App'
import './ComplaintResults.css'

interface Props {
  complaint: Complaint
}

export default function ComplaintResults({ complaint }: Props) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="results-card">
      <h2>Complaint Analysis</h2>

      <div className="results-section">
        <div className="result-item">
          <span className="result-label">Complaint ID:</span>
          <span className="result-value">{complaint.complaint_id}</span>
        </div>

        <div className="result-item">
          <span className="result-label">Complaint Text:</span>
          <div className="result-text">{complaint.complaint_text}</div>
        </div>

        {complaint.summary && (
          <div className="result-item summary-item">
            <span className="result-label">AI Summary:</span>
            <div className="result-summary">{complaint.summary}</div>
          </div>
        )}

        <div className="categories-grid">
          {complaint.product && (
            <div className="category-card">
              <div className="category-label">Product</div>
              <div className="category-value">{complaint.product}</div>
            </div>
          )}

          {complaint.sub_product && (
            <div className="category-card">
              <div className="category-label">Sub-Product</div>
              <div className="category-value">{complaint.sub_product}</div>
            </div>
          )}

          {complaint.issue && (
            <div className="category-card">
              <div className="category-label">Issue</div>
              <div className="category-value">{complaint.issue}</div>
            </div>
          )}

          {complaint.sub_issue && (
            <div className="category-card">
              <div className="category-label">Sub-Issue</div>
              <div className="category-value">{complaint.sub_issue}</div>
            </div>
          )}
        </div>

        {(complaint.company || complaint.state) && (
          <div className="metadata-row">
            {complaint.company && (
              <div className="metadata-item">
                <span className="metadata-label">Company:</span>
                <span className="metadata-value">{complaint.company}</span>
              </div>
            )}
            {complaint.state && (
              <div className="metadata-item">
                <span className="metadata-label">State:</span>
                <span className="metadata-value">{complaint.state}</span>
              </div>
            )}
          </div>
        )}

        <div className="result-item">
          <span className="result-label">Processed:</span>
          <span className="result-value">{formatDate(complaint.created_at)}</span>
        </div>
      </div>
    </div>
  )
}
