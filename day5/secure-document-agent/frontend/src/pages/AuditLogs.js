import React, { useState, useEffect } from 'react';
import { Activity, Filter, Download, Search } from 'lucide-react';
import api from '../services/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadAuditLogs();
  }, [filter]);

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { category: filter } : {};
      const response = await api.get('/audit/logs', { params });
      setLogs(response.data.logs || []);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
      // For demo purposes, create some mock logs
      setLogs([
        {
          timestamp: new Date().toISOString(),
          event_type: 'document_uploaded',
          category: 'document',
          severity: 'info',
          source: 'document_agent',
          data: { filename: 'test_document.txt', user_id: 'demo_user' }
        },
        {
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          event_type: 'security_scan',
          category: 'security',
          severity: 'info',
          source: 'security_scanner',
          data: { scan_result: 'clean', threats_found: 0 }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getEventIcon = (category) => {
    switch (category) {
      case 'security': return '🛡️';
      case 'document': return '📄';
      case 'compliance': return '⚖️';
      default: return '📋';
    }
  };

  const filteredLogs = logs.filter(log =>
    searchTerm === '' ||
    log.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.data?.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.data?.user_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="audit-logs">
      <div className="audit-header">
        <div className="audit-title">
          <Activity size={32} />
          <div>
            <h1>Audit Logs</h1>
            <p>Security and compliance event tracking</p>
          </div>
        </div>
        
        <button className="btn btn-outline">
          <Download size={16} />
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <div className="audit-filters">
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          {['all', 'security', 'document', 'compliance'].map(category => (
            <button
              key={category}
              onClick={() => setFilter(category)}
              className={`filter-tab ${filter === category ? 'active' : ''}`}
            >
              {category === 'all' ? 'All Events' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Logs List */}
      {loading ? (
        <div className="logs-loading">
          <div className="loading-spinner"></div>
          <p>Loading audit logs...</p>
        </div>
      ) : (
        <div className="logs-list">
          {filteredLogs.length === 0 ? (
            <div className="no-logs">
              <Activity size={48} />
              <h3>No audit logs found</h3>
              <p>No events match your current filters</p>
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div key={index} className="log-entry">
                <div className="log-icon">
                  <span style={{ color: getSeverityColor(log.severity) }}>
                    {getEventIcon(log.category)}
                  </span>
                </div>
                
                <div className="log-content">
                  <div className="log-header">
                    <h4>{log.event_type.replace(/_/g, ' ').toUpperCase()}</h4>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="log-details">
                    <span className={`log-category ${log.category}`}>
                      {log.category}
                    </span>
                    <span className={`log-severity ${log.severity}`}>
                      {log.severity}
                    </span>
                    <span className="log-source">
                      {log.source}
                    </span>
                  </div>
                  
                  {log.data && Object.keys(log.data).length > 0 && (
                    <div className="log-data">
                      {Object.entries(log.data).map(([key, value]) => (
                        <div key={key} className="log-data-item">
                          <span className="data-key">{key}:</span>
                          <span className="data-value">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default AuditLogs;
