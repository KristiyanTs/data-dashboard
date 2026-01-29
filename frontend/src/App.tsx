import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './components/Dashboard';
import { ContractList } from './components/ContractList';
import { ContractForm } from './components/ContractForm';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

type Tab = 'dashboard' | 'list' | 'create';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <header className="app-header">
          <h1>Procurement Data Dashboard</h1>
          <nav className="tabs">
            <button 
              className={activeTab === 'dashboard' ? 'active' : ''} 
              onClick={() => setActiveTab('dashboard')}
            >
              Dashboard
            </button>
            <button 
              className={activeTab === 'list' ? 'active' : ''} 
              onClick={() => setActiveTab('list')}
            >
              Contracts
            </button>
            <button 
              className={activeTab === 'create' ? 'active' : ''} 
              onClick={() => setActiveTab('create')}
            >
              Create Contract
            </button>
          </nav>
        </header>

        <main className="app-content">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'list' && <ContractList />}
          {activeTab === 'create' && <ContractForm />}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
