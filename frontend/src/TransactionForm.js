import React, { useState } from 'react';
import axios from 'axios';
import { CreditCard, Send, CheckCircle, XCircle, Loader } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

const GATEWAYS = ['razorpay', 'stripe', 'paytm', 'phonepe'];

function TransactionForm({ merchants, onTransactionCreated }) {
  const [formData, setFormData] = useState({
    merchant_id: '',
    amount: '',
    currency: 'INR',
    gateway: 'razorpay',
    customer_email: '',
    customer_phone: ''
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
      const response = await axios.post(`${API_BASE_URL}/transactions`, {
        ...formData,
        amount: parseFloat(formData.amount)
      });

      setResult({
        success: true,
        data: response.data
      });

      // Reset form
      setFormData({
        merchant_id: '',
        amount: '',
        currency: 'INR',
        gateway: 'razorpay',
        customer_email: '',
        customer_phone: ''
      });

      // Notify parent component
      onTransactionCreated();
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.detail || 'Transaction failed'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="transaction-form-container">
      <div className="form-header">
        <CreditCard size={32} />
        <h2>Process Payment</h2>
        <p>Create a new payment transaction</p>
      </div>

      <form onSubmit={handleSubmit} className="transaction-form">
        <div className="form-group">
          <label htmlFor="merchant_id">Merchant *</label>
          <select
            id="merchant_id"
            name="merchant_id"
            value={formData.merchant_id}
            onChange={handleChange}
            required
          >
            <option value="">Select Merchant</option>
            {merchants.map((merchant) => (
              <option key={merchant.id} value={merchant.merchant_id}>
                {merchant.merchant_name} ({merchant.merchant_id})
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="amount">Amount *</label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              min="1"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="currency">Currency</label>
            <select
              id="currency"
              name="currency"
              value={formData.currency}
              onChange={handleChange}
            >
              <option value="INR">INR</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="gateway">Payment Gateway *</label>
          <div className="gateway-options">
            {GATEWAYS.map((gateway) => (
              <label key={gateway} className="gateway-option">
                <input
                  type="radio"
                  name="gateway"
                  value={gateway}
                  checked={formData.gateway === gateway}
                  onChange={handleChange}
                />
                <span className="gateway-name">{gateway}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="customer_email">Customer Email *</label>
          <input
            type="email"
            id="customer_email"
            name="customer_email"
            value={formData.customer_email}
            onChange={handleChange}
            placeholder="customer@example.com"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customer_phone">Customer Phone</label>
          <input
            type="tel"
            id="customer_phone"
            name="customer_phone"
            value={formData.customer_phone}
            onChange={handleChange}
            placeholder="+91 9876543210"
          />
        </div>

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? (
            <>
              <Loader className="spinning" size={20} />
              Processing...
            </>
          ) : (
            <>
              <Send size={20} />
              Process Payment
            </>
          )}
        </button>
      </form>

      {/* Result Display */}
      {result && (
        <div className={`result-card ${result.success ? 'success' : 'error'}`}>
          <div className="result-icon">
            {result.success ? (
              <CheckCircle size={48} />
            ) : (
              <XCircle size={48} />
            )}
          </div>
          <div className="result-content">
            {result.success ? (
              <>
                <h3>Transaction Successful!</h3>
                <div className="result-details">
                  <p><strong>Transaction ID:</strong> {result.data.transaction_id}</p>
                  <p><strong>Amount:</strong> ₹{result.data.amount}</p>
                  <p><strong>Gateway:</strong> {result.data.gateway}</p>
                  <p><strong>Status:</strong> <span className={`status-badge ${result.data.status}`}>{result.data.status}</span></p>
                </div>
              </>
            ) : (
              <>
                <h3>Transaction Failed</h3>
                <p className="error-message">{result.error}</p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default TransactionForm;