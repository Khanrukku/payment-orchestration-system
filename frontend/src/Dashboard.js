import React from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

import { TrendingUp, DollarSign, CheckCircle, XCircle, Clock, Users } from 'lucide-react';

const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6'];

function Dashboard({ stats, transactions, merchants }) {
  // Calculate gateway distribution
  const gatewayData = transactions.reduce((acc, txn) => {
    const existing = acc.find(item => item.name === txn.gateway);
    if (existing) {
      existing.value += 1;
    } else {
      acc.push({ name: txn.gateway, value: 1 });
    }
    return acc;
  }, []);

  // Calculate status distribution for pie chart
  const statusData = [
    { name: 'Success', value: stats?.successful_transactions || 0, color: '#10b981' },
    { name: 'Failed', value: stats?.failed_transactions || 0, color: '#ef4444' },
    { name: 'Pending', value: stats?.pending_transactions || 0, color: '#f59e0b' }
  ].filter(item => item.value > 0);

  // Recent transactions (last 5)
  const recentTransactions = transactions.slice(0, 5);

  return (
    <div className="dashboard">
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon total">
            <TrendingUp size={24} />
          </div>
          <div className="stat-info">
            <p className="stat-label">Total Transactions</p>
            <h2 className="stat-number">{stats?.total_transactions || 0}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success">
            <CheckCircle size={24} />
          </div>
          <div className="stat-info">
            <p className="stat-label">Successful</p>
            <h2 className="stat-number">{stats?.successful_transactions || 0}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon failed">
            <XCircle size={24} />
          </div>
          <div className="stat-info">
            <p className="stat-label">Failed</p>
            <h2 className="stat-number">{stats?.failed_transactions || 0}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon volume">
            <DollarSign size={24} />
          </div>
          <div className="stat-info">
            <p className="stat-label">Total Volume</p>
            <h2 className="stat-number">₹{stats?.total_volume?.toFixed(2) || 0}</h2>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        {/* Gateway Performance Bar Chart */}
        <div className="chart-card">
          <h3>Gateway Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={gatewayData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="Transactions" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution Pie Chart */}
        <div className="chart-card">
          <h3>Transaction Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="recent-transactions">
        <h3>Recent Transactions</h3>
        <div className="table-container">
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Merchant</th>
                <th>Amount</th>
                <th>Gateway</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.length > 0 ? (
                recentTransactions.map((txn) => (
                  <tr key={txn.id}>
                    <td className="transaction-id">{txn.transaction_id}</td>
                    <td>{txn.merchant_id}</td>
                    <td className="amount">₹{txn.amount.toFixed(2)}</td>
                    <td>
                      <span className="gateway-badge">{txn.gateway}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${txn.status}`}>
                        {txn.status}
                      </span>
                    </td>
                    <td className="date">{new Date(txn.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="no-data">No transactions yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Merchants Summary */}
      <div className="merchants-summary">
        <h3>Active Merchants</h3>
        <div className="merchant-count">
          <Users size={48} />
          <span className="count">{merchants.length}</span>
          <span className="label">Total Merchants</span>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;