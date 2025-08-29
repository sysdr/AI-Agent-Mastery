import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Upload, FileText, Shield, AlertTriangle, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import api from '../services/api';

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    withPii: 0,
    highRisk: 0,
    processed: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/documents');
      const docs = response.data;
      setDocuments(docs);
      
      // Calculate statistics
      const stats = {
        total: docs.length,
        withPii: docs.filter(doc => doc.has_pii).length,
        highRisk: docs.filter(doc => doc.risk_level === 'high').length,
        processed: docs.filter(doc => doc.created_at).length
      };
      setStats(stats);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const riskData = [
    { name: 'Low Risk', value: documents.filter(d => d.risk_level === 'low').length, color: '#10b981' },
    { name: 'Medium Risk', value: documents.filter(d => d.risk_level === 'medium').length, color: '#f59e0b' },
    { name: 'High Risk', value: documents.filter(d => d.risk_level === 'high').length, color: '#ef4444' },
  ];

  const processingData = [
    { name: 'Today', processed: 12 },
    { name: 'Yesterday', processed: 8 },
    { name: '2 days ago', processed: 15 },
    { name: '3 days ago', processed: 7 },
    { name: '4 days ago', processed: 11 },
    { name: '5 days ago', processed: 9 },
    { name: '6 days ago', processed: 13 },
  ];

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Document Security Dashboard</h1>
        <Link to="/upload" className="btn btn-primary">
          <Upload size={20} />
          Upload Document
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <FileText size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats.total}</h3>
            <p>Total Documents</p>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">
            <Shield size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats.withPii}</h3>
            <p>Contains PII</p>
          </div>
        </div>

        <div className="stat-card danger">
          <div className="stat-icon">
            <AlertTriangle size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats.highRisk}</h3>
            <p>High Risk</p>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">
            <Clock size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats.processed}</h3>
            <p>Processed Today</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Document Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Processing Activity (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={processingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="processed" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Documents */}
      <div className="recent-documents">
        <h3>Recent Documents</h3>
        <div className="documents-list">
          {documents.slice(0, 5).map(doc => (
            <Link to={`/document/${doc.document_id}`} key={doc.document_id} className="document-item">
              <div className="document-info">
                <h4>{doc.filename}</h4>
                <p>{new Date(doc.created_at).toLocaleDateString()}</p>
              </div>
              <div className="document-badges">
                {doc.has_pii && <span className="badge warning">PII</span>}
                <span className={`badge ${doc.risk_level}`}>{doc.risk_level} risk</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
