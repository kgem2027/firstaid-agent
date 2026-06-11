import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../middleware/authProvider.jsx'

export default function History() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  function getHistory() {
    setLoading(true)
    setError('')
    axios.get('/api/history/')
      .then(res => setHistory(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load history.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    getHistory()
  }, [])

  function toggleExpand(id) {
    setExpandedId(prev => prev === id ? null : id)
  }

  return (
    <div className="max-w-2xl mx-auto mt-10 p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/analyze')}
            className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
          >
            ← Back
          </button>
          <h1 className="text-2xl font-bold">Past Analyses</h1>
        </div>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Logout
        </button>
      </div>

      {loading && (
        <p className="text-gray-500 text-sm">Loading history…</p>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {!loading && !error && history.length === 0 && (
        <p className="text-gray-400 text-sm">No past analyses yet.</p>
      )}

      <div className="flex flex-col gap-4">
        {history.map((record) => {
          const isExpanded = expandedId === record.id
          return (
            <div key={record.id} className="bg-white border rounded-2xl shadow-sm overflow-hidden">

              {/* Summary row — always visible, click to toggle */}
              <button
                onClick={() => toggleExpand(record.id)}
                className="w-full text-left p-5 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start mb-2">
                  <h2 className="font-semibold text-lg">{record.condition}</h2>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{record.country}</span>
                    <span className="text-gray-400 text-sm">{isExpanded ? '▲' : '▼'}</span>
                  </div>
                </div>

                <p className="text-sm text-gray-500 mb-3 italic">"{record.symptoms}"</p>

                <div className="flex flex-wrap gap-2 mb-3">
                  {record.compoundKeywords.map((kw, i) => (
                    <span key={i} className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                      {kw}
                    </span>
                  ))}
                </div>

                <p className="text-xs text-gray-400">
                  {record.remedyPlants.length} remedy plant{record.remedyPlants.length !== 1 ? 's' : ''} — click to {isExpanded ? 'collapse' : 'view'}
                </p>
              </button>

              {/* Expanded plant list */}
              {isExpanded && (
                <div className="border-t px-5 pb-5 pt-4 flex flex-col gap-3">
                  {record.remedyPlants.map((plant, i) => (
                    <div key={i} className="p-4 border rounded-xl">
                      <div className="flex justify-between items-start">
                        <h3 className="font-semibold">{plant.commonName}</h3>
                        <span className="text-xs text-blue-500">{plant.source}</span>
                      </div>
                      <p className="text-sm text-gray-400 italic mb-2">{plant.pharmacopoeialName}</p>
                      <ul className="list-disc list-inside text-sm text-gray-600 space-y-0.5">
                        {(plant.matchingUses ?? []).map((use, j) => (
                          <li key={j}>{use}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
