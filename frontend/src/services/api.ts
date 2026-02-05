import axios from 'axios'
import { Complaint, SimilarComplaint } from '../App'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ComplaintCreateRequest {
  complaint_text: string
  product?: string
  sub_product?: string
  company?: string
  state?: string
  zip_code?: string
}

export interface SimilarComplaintsRequest {
  complaint_text?: string
  complaint_id?: string
  top_k?: number
  similarity_threshold?: number
}

export interface SimilarComplaintsResponse {
  query_complaint_id: string | null
  similar_complaints: SimilarComplaint[]
  total_found: number
}

export const complaintApi = {
  // Submit a new complaint
  async createComplaint(data: ComplaintCreateRequest): Promise<Complaint> {
    const response = await api.post<Complaint>('/complaints/', data)
    return response.data
  },

  // Get complaint by ID
  async getComplaint(complaintId: string): Promise<Complaint> {
    const response = await api.get<Complaint>(`/complaints/${complaintId}`)
    return response.data
  },

  // Find similar complaints
  async findSimilarComplaints(
    request: SimilarComplaintsRequest
  ): Promise<SimilarComplaintsResponse> {
    const response = await api.post<SimilarComplaintsResponse>(
      '/search/similar',
      request
    )
    return response.data
  },

  // Get system statistics
  async getStats() {
    const response = await api.get('/search/stats')
    return response.data
  },
}

export default api
