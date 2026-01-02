import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ChatWindow } from './components/Chat/ChatWindow'
import { LoginPage } from './components/Login/LoginPage'
import { ProtectedRoute } from './components/Auth/ProtectedRoute'
import { PublicRoute } from './components/Auth/PublicRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicRoute />}>
          <Route path="/" element={<LoginPage />} />
        </Route>
        <Route element={<ProtectedRoute />}>
          <Route path="/chat" element={<ChatWindow />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
