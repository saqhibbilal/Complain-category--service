import { useState } from 'react'
import ComplaintSubmissionForm from './components/ComplaintSubmissionForm'
import ComplaintResults from './components/ComplaintResults'
import SimilarComplaintsList from './components/SimilarComplaintsList'
import './App.css'

export interface Complaint {
  id: string
  complaint_id: string
  complaint_text: string
  product: string | null
  sub_product: string | null
  issue: string | null
  sub_issue: string | null
  company: string | null
  state: string | null
  summary: string | null
  created_at: string
}

export interface SimilarComplaint {
  complaint: Complaint
  similarity_score: number
}

function App() {
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
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>Complaint Categorization System</h1>
          <p className="subtitle">AI-powered complaint analysis with RAG</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
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
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>Complaint Categorization & RAG System v1.0</p>
        </div>
      </footer>
    </div>
  )
}

export default App
