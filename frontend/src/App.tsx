import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import HomePage from './pages/HomePage'
import Dashboard from './components/Dashboard'
import ComplaintsList from './components/ComplaintsList'
import ComplaintDetail from './components/ComplaintDetail'
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
  return (
    <Router>
      <div className="app">
        <Navigation />
        
        <main className="app-main">
          <div className="container">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/complaints" element={<ComplaintsList />} />
              <Route path="/complaints/:id" element={<ComplaintDetail />} />
            </Routes>
          </div>
        </main>

        <footer className="app-footer">
          <div className="container">
            <p>Complaint Categorization & RAG System v1.0</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
