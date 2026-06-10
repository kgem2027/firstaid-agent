import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../middleware/authProvider.jsx'

export default function Analyze() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ image: null, symptoms: '', country: '' })
  const [preview, setPreview] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleLogout() {
    logout()
    navigate('/login')
  }
  function handleHistory() {
    navigate('/history')
  }

  function handleChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  function handleImage(e) {
    const file = e.target.files[0]
    if (!file) return
    setForm(prev => ({ ...prev, image: file }))
    setPreview(URL.createObjectURL(file))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const formData = new FormData()
      formData.append('image', form.image)
      formData.append('symptoms', form.symptoms)
      formData.append('country', form.country)
      const res = await axios.post('/api/analyze/', formData)
      setResults(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto mt-10 p-6 bg-white rounded-2xl shadow">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Plant Analyzer</h1>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Logout
        </button>
        <button
          onClick={handleHistory}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          History
        </button>
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">

        <div className="flex flex-col gap-1">
          <label htmlFor="country" className="font-medium">Country</label>
          <input
            id="country"
            name="country"
            type="text"
            placeholder="e.g. India, Brazil"
            value={form.country}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="symptoms" className="font-medium">Symptom / Observation</label>
          <textarea
            id="symptoms"
            name="symptoms"
            rows={4}
            placeholder="Describe the symptom or observation..."
            value={form.symptoms}
            onChange={handleChange}
            className="border rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="image" className="font-medium">Plant Image</label>
          <input
            id="image"
            name="image"
            type="file"
            accept="image/*"
            onChange={handleImage}
            className="border rounded-lg px-3 py-2 file:mr-3 file:rounded file:border-0 file:bg-green-50 file:px-3 file:py-1 file:text-green-700 cursor-pointer"
          />
          {preview && (
            <img
              src={preview}
              alt="Preview"
              className="mt-2 rounded-lg max-h-48 object-cover"
            />
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white font-semibold rounded-lg py-2 transition-colors"
        >
          {loading ? 'Analyzing… this may take up to 60 seconds' : 'Analyze'}
        </button>
      </form>

      {loading && (
        <div className="mt-8 flex flex-col items-center gap-4 text-gray-500">
          <div className="w-10 h-10 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
          <p className="text-sm">Analyzing… this can take up to a minute</p>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {results && (
        <div className="mt-8 flex flex-col gap-6">
          <div>
            <h2 className="text-xl font-bold">Condition</h2>
            <p className="mt-1">{results.condition}</p>
          </div>

          <div>
            <h2 className="text-xl font-bold">Keywords</h2>
            <div className="flex flex-wrap gap-2 mt-1">
              {(results.compoundKeywords ?? []).map((kw, i) => (
                <span key={i} className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">{kw}</span>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3">Remedy Plants</h2>
            {(results.remedyPlants ?? []).map((plant, i) => (
              <div key={i} className="p-4 border rounded-xl mb-3">
                <h3 className="font-semibold text-lg">{plant.commonName}</h3>
                <p className="text-sm text-gray-500 italic">{plant.pharmacopoeialName}</p>
                <p className="text-xs mt-1 text-blue-600">{plant.source}</p>
                <ul className="list-disc list-inside mt-2 text-sm">
                  {plant.matchingUses.map((use, j) => (
                    <li key={j}>{use}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
