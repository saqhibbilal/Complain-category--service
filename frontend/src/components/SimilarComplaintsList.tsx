import { SimilarComplaint } from '../App'
import './SimilarComplaintsList.css'

interface Props {
  similarComplaints: SimilarComplaint[]
}

export default function SimilarComplaintsList({ similarComplaints }: Props) {
  const formatScore = (score: number) => {
    return (score * 100).toFixed(1)
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'high'
    if (score >= 0.6) return 'medium'
    return 'low'
  }

  return (
    <div className="similar-complaints-container">
      <h2>Similar Complaints</h2>
      <p className="similar-description">
        Found {similarComplaints.length} similar complaint{similarComplaints.length !== 1 ? 's' : ''} based on similarity analysis
      </p>

      {similarComplaints.length === 0 ? (
        <div className="no-similar">
          <p>No similar complaints found.</p>
        </div>
      ) : (
        <div className="similar-complaints-grid">
          {similarComplaints.map((item, index) => (
            <div key={item.complaint.id} className="similar-complaint-card">
              <div className="card-header">
                <div className="card-number">#{index + 1}</div>
                <div className={`similarity-badge ${getScoreColor(item.similarity_score)}`}>
                  {formatScore(item.similarity_score)}% Match
                </div>
              </div>

              <div className="card-content">
                <div className="complaint-preview">
                  {item.complaint.complaint_text.length > 200
                    ? `${item.complaint.complaint_text.substring(0, 200)}...`
                    : item.complaint.complaint_text}
                </div>

                {item.complaint.summary && (
                  <div className="complaint-summary">
                    <strong>Summary:</strong> {item.complaint.summary}
                  </div>
                )}

                <div className="complaint-meta">
                  {item.complaint.product && (
                    <span className="meta-tag product">
                      {item.complaint.product}
                    </span>
                  )}
                  {item.complaint.sub_product && (
                    <span className="meta-tag sub-product">
                      {item.complaint.sub_product}
                    </span>
                  )}
                  {item.complaint.company && (
                    <span className="meta-tag company">
                      {item.complaint.company}
                    </span>
                  )}
                </div>
              </div>

              <div className="card-footer">
                <div className="complaint-id">
                  ID: {item.complaint.complaint_id}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
