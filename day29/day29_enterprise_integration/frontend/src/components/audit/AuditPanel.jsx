import React, { useState, useEffect } from 'react';
import { FileText, Filter } from 'lucide-react';
import { api } from '../../services/api';

const AuditPanel = () => {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditEvents();
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvents = filter
    ? events.filter(e => e.event_type.toLowerCase().includes(filter.toLowerCase()))
    : events;

  return (
    <div className="audit-panel">
      <div className="audit-header">
        <h2>
          <FileText size={24} />
          Audit Event Log
        </h2>
        <div className="audit-controls">
          <input
            type="text"
            placeholder="Filter by event type..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-input"
          />
          <button className="btn" onClick={loadEvents}>
            <Filter size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="audit-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event Type</th>
              <th>Aggregate ID</th>
              <th>Correlation ID</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.map((event) => (
              <tr key={event.event_id}>
                <td>{new Date(event.timestamp).toLocaleString()}</td>
                <td>
                  <span className="event-badge">{event.event_type}</span>
                </td>
                <td><code>{event.aggregate_id}</code></td>
                <td><code className="correlation-id">{event.correlation_id || 'N/A'}</code></td>
                <td>
                  <details>
                    <summary>View Data</summary>
                    <pre>{JSON.stringify(event.data, null, 2)}</pre>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredEvents.length === 0 && (
          <div className="empty-state">
            <p>No audit events found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditPanel;
