import './App.css'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from "../middleware/authProvider.jsx"
import Analyze from "../pages/Analyze"
import Login from "../pages/Login"
import Register from "../pages/Register"
import History from '../pages/History.jsx'


function PrivateRoute({ children }) {
  const { user } = useAuth()
  const location = useLocation()
  return user ? children : <Navigate to="/login" state={{ from: location }} replace />
}

function AppContent() {
  const { user } = useAuth()

  return (
    <div className="App">
      <Routes>
        <Route path="/analyze" element={<PrivateRoute><Analyze /></PrivateRoute>} />
        <Route path="/history" element={<PrivateRoute><History /></PrivateRoute>} />
        <Route path="/login" element={!user ? <Login /> : <Navigate to="/analyze" />} />
        <Route path="/register" element={!user ? <Register /> : <Navigate to="/analyze" />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  )
}

export default App
