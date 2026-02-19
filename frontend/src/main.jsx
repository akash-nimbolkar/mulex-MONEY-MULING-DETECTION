import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import Home from './pages/Home'
import Analysis from './pages/Analysis'
import Network from './pages/analysis/Network'
import Rings from './pages/analysis/Rings'
import Accounts from './pages/analysis/Accounts'
import './styles.css'

createRoot(document.getElementById('root')).render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Home />} />
          <Route path="analysis" element={<Analysis />}>
            <Route index element={<Network />} />
            <Route path="network" element={<Network />} />
            <Route path="fraud" element={<Rings />} />
            <Route path="accounts" element={<Accounts />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
)
