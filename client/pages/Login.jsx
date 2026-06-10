import { useState } from 'react'
import axios from 'axios'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../middleware/authProvider.jsx'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post('/api/auth/login', formData)
      login(res.data.user, res.data.token)
      navigate('/analyze')
    } catch (error) {
      setErrors(error.response?.data?.message || 'An error occurred during login.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-md p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Welcome back</h2>
        <p className="text-sm text-gray-500 mb-6">Sign in to your account</p>

        {errors && (
          <div className="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {errors}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="email" className="text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="password" className="text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>

          <button
            type="submit"
            className="mt-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg py-2 text-sm transition-colors"
          >
            Sign in
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-green-600 hover:text-green-700 font-medium">
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
