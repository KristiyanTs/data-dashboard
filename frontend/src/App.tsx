import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Dashboard } from './components/Dashboard';
import { ContractList } from './components/ContractList';
import { ContractForm } from './components/ContractForm';
import { Scraper } from './components/Scraper';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="top-right" />
      <div className="App">
        <header className="app-header">
          <div className="app-header-inner">
            <h1 className="app-logo">Procurement Dashboard</h1>
            <nav className="app-nav" aria-label="Main">
              <NavLink
                to="/"
                end
                className={({ isActive }) => (isActive ? 'active' : '')}
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/contracts"
                className={({ isActive }) => (isActive ? 'active' : '')}
              >
                Contracts
              </NavLink>
              <NavLink
                to="/scraper"
                className={({ isActive }) => (isActive ? 'active' : '')}
              >
                Scraper
              </NavLink>
              <NavLink
                to="/contracts/new"
                className={({ isActive }) => (isActive ? 'active' : '')}
              >
                New contract
              </NavLink>
            </nav>
          </div>
        </header>

        <main className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts" element={<ContractList />} />
            <Route path="/scraper" element={<Scraper />} />
            <Route path="/contracts/new" element={<ContractForm />} />
          </Routes>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
