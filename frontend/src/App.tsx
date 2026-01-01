import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ChatWindow } from './components/Chat/ChatWindow'
import { LoginPage } from './components/Login/LoginPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/chat" element={<ChatWindow />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
