import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './Dashboard';
import TransactionForm from './TransactionForm';
import MerchantList from './MerchantList';
import './App.css';
import { Activity, CreditCard, Users, BarChart3 } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [merchants, setMerchants] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch merchants
  const fetchMerchants = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/merchants`);
      setMerchants(response.data);
    } catch (error) {
      console.error('Error fetching merchants:', error);
    }
  };

  // Fetch transactions
  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchMerchants();
    fetchTransactions();
    fetchStats();
  }, []);

  // Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTransactions();
      fetchStats();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleTransactionCreated = () => {
    fetchTransactions();
    fetchStats();
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <Activity className="logo-icon" size={32} />
            <h1>Payment Orchestration System</h1>
          </div>
          <div className="header-stats">
            <div className="stat-badge">
              <span className="stat-value">{stats?.total_transactions || 0}</span>
              <span className="stat-label">Transactions</span>
            </div>
            <div className="stat-badge success">
              <span className="stat-value">{stats?.success_rate || 0}%</span>
              <span className="stat-label">Success Rate</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <BarChart3 size={20} />
          Dashboard
        </button>
        <button
          className={`nav-tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          <CreditCard size={20} />
          Create Transaction
        </button>
        <button
          className={`nav-tab ${activeTab === 'merchants' ? 'active' : ''}`}
          onClick={() => setActiveTab('merchants')}
        >
          <Users size={20} />
          Merchants
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard 
            stats={stats} 
            transactions={transactions}
            merchants={merchants}
          />
        )}
        
        {activeTab === 'transactions' && (
          <TransactionForm
            merchants={merchants}
            onTransactionCreated={handleTransactionCreated}
          />
        )}
        
        {activeTab === 'merchants' && (
          <MerchantList
            merchants={merchants}
            onMerchantAdded={fetchMerchants}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Payment Orchestration System v1.0.0 | Processing payments securely</p>
      </footer>
    </div>
  );
}

export default App;