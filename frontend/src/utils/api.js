import axios from 'axios'

// Configure base URL - change based on environment
// For Vite, use import.meta.env instead of process.env
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// API Functions for Backend Integration

/**
 * Upload CSV file to backend for analysis
 * @param {File} file - CSV file to upload
 * @returns {Promise} Response from backend
 */
export async function uploadCSV(file) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
    
    return { success: true, data: response.data }
  } catch (error) {
    console.error('Upload error:', error)
    return { success: false, error: error.response?.data?.error || error.message }
  }
}

/**
 * Run analysis on uploaded CSV
 * @returns {Promise} Analysis results from backend
 */
export async function runAnalysis() {
  try {
    const response = await api.post('/analyze')
    return { success: true, data: response.data }
  } catch (error) {
    console.error('Analysis error:', error)
    return { success: false, error: error.response?.data?.error || error.message }
  }
}

/**
 * Get analysis results (graph, rings, accounts, summary)
 * @returns {Promise} Visualization data and analysis results
 */
export async function getResults() {
  try {
    const response = await api.get('/results')
    return { success: true, data: response.data }
  } catch (error) {
    console.error('Results error:', error)
    return { success: false, error: error.response?.data?.error || error.message }
  }
}

/**
 * Download results as RIFT-spec JSON
 * @returns {Promise} Downloads JSON file
 */
export async function downloadJSON() {
  try {
    const response = await api.get('/download-json', {
      responseType: 'blob'
    })
    
    // Create download link
    const blob = new Blob([response.data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analysis_results_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
    
    return { success: true }
  } catch (error) {
    console.error('Download error:', error)
    return { success: false, error: error.response?.data?.error || error.message }
  }
}

export default api
