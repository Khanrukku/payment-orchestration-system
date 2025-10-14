import React, { useState } from 'react';
import axios from 'axios';
import { Users, Plus, Store, Mail, Key, CheckCircle, XCircle } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

function MerchantList({ merchants, onMerchantAdded }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    merchant_name: '',
    email: '',
    preferred_gateway: 'razorpay'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/merchants`, formData);
      
      setResult({
        success: true,
        data: response.data
      });

      // Reset form
      setFormData({
        merchant_name: '',
        email: '',
        preferred_gateway: 'razorpay'
      });

      // Notify parent
      onMerchantAdded();

      // Close form after 3 seconds
      setTimeout(() => {
        setShowForm(false);
        setResult(null);
      }, 3000);
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.detail || 'Failed to create merchant'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="merchant-list-container">
      <div className="list-header">
        <div>
          <h2>Merchant Management</h2>
          <p>Manage merchant accounts and view details</p>
        </div>
        <button 
          className="add-merchant-button"
          onClick={() => setShowForm(!showForm)}
        >
          <Plus size={20} />
          Add Merchant
        </button>
      </div>

      {/* Add Merchant Form */}
      {showForm && (
        <div className="merchant-form-card">
          <h3>Create New Merchant</h3>
          <form onSubmit={handleSubmit} className="merchant-form">
            <div className="form-group">
              <label htmlFor="merchant_name">Merchant Name *</label>
              <input
                type="text"
                id="merchant_name"
                name="merchant_name"
                value={formData.merchant_name}
                onChange={handleChange}
                placeholder="Enter merchant name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="merchant@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="preferred_gateway">Preferred Gateway</label>
              <select
                id="preferred_gateway"
                name="preferred_gateway"
                value={formData.preferred_gateway}
                onChange={handleChange}
              >
                <option value="razorpay">Razorpay</option>
                <option value="stripe">Stripe</option>
                <option value="paytm">Paytm</option>
                <option value="phonepe">PhonePe</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="button" onClick={() => setShowForm(false)} className="cancel-button">
                Cancel
              </button>
              <button type="submit" className="submit-button" disabled={loading}>
                {loading ? 'Creating...' : 'Create Merchant'}
              </button>
            </div>
          </form>

          {result && (
            <div className={`result-message ${result.success ? 'success' : 'error'}`}>
              {result.success ? (
                <>
                  <CheckCircle size={20} />
                  <span>Merchant created successfully!</span>
                </>
              ) : (
                <>
                  <XCircle size={20} />
                  <span>{result.error}</span>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Merchants Grid */}
      <div className="merchants-grid">
        {merchants.length > 0 ? (
          merchants.map((merchant) => (
            <div key={merchant.id} className="merchant-card">
              <div className="merchant-header">
                <div className="merchant-icon">
                  <Store size={24} />
                </div>
                <div className="merchant-status">
                  {merchant.is_active ? (
                    <span className="status-badge success">Active</span>
                  ) : (
                    <span className="status-badge failed">Inactive</span>
                  )}
                </div>
              </div>

              <h3 className="merchant-name">{merchant.merchant_name}</h3>
              
              <div className="merchant-details">
                <div className="detail-item">
                  <Key size={16} />
                  <span className="detail-label">ID:</span>
                  <span className="detail-value">{merchant.merchant_id}</span>
                </div>

                <div className="detail-item">
                  <Mail size={16} />
                  <span className="detail-label">Email:</span>
                  <span className="detail-value">{merchant.email}</span>
                </div>

                <div className="detail-item">
                  <Users size={16} />
                  <span className="detail-label">Gateway:</span>
                  <span className="gateway-badge">{merchant.preferred_gateway}</span>
                </div>
              </div>

              <div className="merchant-footer">
                <div className="api-key-section">
                  <span className="api-key-label">API Key:</span>
                  <code className="api-key">{merchant.api_key}</code>
                </div>
                <small className="created-date">
                  Created: {new Date(merchant.created_at).toLocaleDateString()}
                </small>
              </div>
            </div>
          ))
        ) : (
          <div className="no-merchants">
            <Users size={64} />
            <h3>No Merchants Yet</h3>
            <p>Click "Add Merchant" to create your first merchant account</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default MerchantList;