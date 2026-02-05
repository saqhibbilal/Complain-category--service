import { useState } from 'react'
import ComplaintSubmissionForm from '../components/ComplaintSubmissionForm'
import ComplaintResults from '../components/ComplaintResults'
import SimilarComplaintsList from '../components/SimilarComplaintsList'
import { Complaint, SimilarComplaint } from '../App'

export default function HomePage() {
  const [submittedComplaint, setSubmittedComplaint] = useState<Complaint | null>(null)
  const [similarComplaints, setSimilarComplaints] = useState<SimilarComplaint[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleComplaintSubmitted = (complaint: Complaint, similar: SimilarComplaint[]) => {
    setSubmittedComplaint(complaint)
    setSimilarComplaints(similar)
  }

  const handleReset = () => {
    setSubmittedComplaint(null)
    setSimilarComplaints([])
  }

  return (
    <div className="home-page">
      {!submittedComplaint ? (
        <ComplaintSubmissionForm
          onSubmitted={handleComplaintSubmitted}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
        />
      ) : (
        <div className="results-container">
          <button className="btn-secondary" onClick={handleReset}>
            ← Submit New Complaint
          </button>
          
          <ComplaintResults complaint={submittedComplaint} />
          
          {similarComplaints.length > 0 && (
            <SimilarComplaintsList similarComplaints={similarComplaints} />
          )}
        </div>
      )}
    </div>
  )
}
