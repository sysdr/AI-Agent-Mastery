import React, { useState, useEffect } from 'react';
import moment from 'moment';
import { tracesAPI } from '../../services/api';

const TracesView = ({ wsData }) => {
  const [traces, setTraces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTrace, setSelectedTrace] = useState(null);

  useEffect(() => {
    const fetchTraces = async () => {
      try {
        const data = await tracesAPI.getAll(50);
        setTraces(data);
      } catch (error) {
        console.error('Error fetching traces:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTraces();
    const interval = setInterval(fetchTraces, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (wsData?.traces) {
      setTraces(wsData.traces);
    }
  }, [wsData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading traces...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Distributed Traces</h2>
        <p className="text-gray-600 mb-4">Real-time trace monitoring and analysis</p>
        <div className="mb-4 text-sm text-gray-500">
          Total traces: {traces.length}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Traces List */}
        <div className="lg:col-span-2 bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Traces</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {traces.length > 0 ? (
              traces.map((trace, index) => (
                <div
                  key={trace.trace_id || index}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedTrace?.trace_id === trace.trace_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedTrace(trace)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">{trace.operation}</span>
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            trace.status === 'success'
                              ? 'bg-green-100 text-green-800'
                              : trace.status === 'active'
                              ? 'bg-blue-100 text-blue-800'
                              : trace.status === 'error'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {trace.status || 'unknown'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        {trace.trace_id?.substring(0, 20)}...
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {trace.start_time
                          ? moment(trace.start_time).format('MMM DD, HH:mm:ss')
                          : 'Unknown time'}
                        {trace.total_duration_ms && ` • ${trace.total_duration_ms.toFixed(2)}ms`}
                      </p>
                    </div>
                  </div>
                  {trace.spans && trace.spans.length > 0 && (
                    <div className="mt-2 text-xs text-gray-500">
                      {trace.spans.length} span{trace.spans.length !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                No traces available
              </div>
            )}
          </div>
        </div>

        {/* Trace Details */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Trace Details</h3>
          {selectedTrace ? (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Operation</label>
                <p className="mt-1 text-sm text-gray-900">{selectedTrace.operation}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Trace ID</label>
                <p className="mt-1 text-sm text-gray-900 font-mono">
                  {selectedTrace.trace_id}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <p className="mt-1">
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      selectedTrace.status === 'success'
                        ? 'bg-green-100 text-green-800'
                        : selectedTrace.status === 'active'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {selectedTrace.status}
                  </span>
                </p>
              </div>
              {selectedTrace.start_time && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Start Time</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {moment(selectedTrace.start_time).format('YYYY-MM-DD HH:mm:ss')}
                  </p>
                </div>
              )}
              {selectedTrace.total_duration_ms && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Duration</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {selectedTrace.total_duration_ms.toFixed(2)}ms
                  </p>
                </div>
              )}
              {selectedTrace.spans && selectedTrace.spans.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Spans</label>
                  <div className="mt-2 space-y-2">
                    {selectedTrace.spans.map((span, idx) => (
                      <div key={idx} className="p-2 bg-gray-50 rounded text-xs">
                        <div className="font-medium">{span.name}</div>
                        {span.duration_ms && (
                          <div className="text-gray-500">{span.duration_ms}ms</div>
                        )}
                        {span.metadata && Object.keys(span.metadata).length > 0 && (
                          <div className="mt-1 text-gray-400">
                            {JSON.stringify(span.metadata)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {selectedTrace.metadata && Object.keys(selectedTrace.metadata).length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Metadata</label>
                  <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-auto">
                    {JSON.stringify(selectedTrace.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 text-sm">
              Select a trace to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TracesView;
