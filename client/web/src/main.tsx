import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { UserProvider, useUser } from './contexts/UserContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import { ReactionsProvider } from './contexts/ReactionsContext'
import { NotFound } from './components/NotFound'

function AppWithWebSocket() {
  const { username, setUsername } = useUser()

  return (
    <WebSocketProvider
      username={username}
      onUsernameAssigned={setUsername}
    >
      <ReactionsProvider>
        <App />
      </ReactionsProvider>
    </WebSocketProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <UserProvider>
        <Routes>
          <Route path="/" element={<AppWithWebSocket />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </UserProvider>
    </BrowserRouter>
  </StrictMode>,
)
