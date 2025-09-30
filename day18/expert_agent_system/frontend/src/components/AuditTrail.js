import React, { useState, useEffect } from 'react';
import { FileText, Clock, CheckCircle } from 'lucide-react';
import moment from 'moment';

const AuditTrail = ({ queryId }) => {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (queryId) {
      fetchAuditTrail(queryId);
    }
  }, [queryId]);

  const fetchAuditTrail = async (id) => {
    setLoading(true);
    try {
      const response = await fetch(`/audit/${id}`);
      if (response.ok) {
        const data = await response.json();
        setAuditData(data);
      }
    } catch (error) {
      console.error('Failed to fetch audit trail:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-300 rounded"></div>
            <div className="h-4 bg-gray-300 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!auditData) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-4">
        <FileText className="text-blue-600 mr-2" size={20} />
        <h3 className="text-lg font-semibold">Audit Trail</h3>
      </div>

      <div className="space-y-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1">Query ID</div>
          <div className="font-mono text-sm">{auditData.query_id}</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1">Timestamp</div>
          <div className="text-sm">{moment(auditData.timestamp).format('LLL')}</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center mb-2">
            <Clock className="text-gray-500 mr-1" size={16} />
            <span className="text-xs text-gray-500">Processing Time</span>
          </div>
          <div className="text-sm font-medium">{auditData.processing_time.toFixed(3)}s</div>
        </div>

        {auditData.validation_steps && auditData.validation_steps.length > 0 && (
          <div>
            <div className="text-sm font-medium text-gray-700 mb-2">Validation Steps</div>
            <div className="space-y-2">
              {auditData.validation_steps.map((step, index) => (
                <div key={index} className="bg-blue-50 rounded p-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-blue-800">
                      {step.step_type?.replace('_', ' ').toUpperCase()}
                    </span>
                    <CheckCircle className="text-blue-600" size={12} />
                  </div>
                  <div className="text-xs text-blue-700">
                    Impact: {(step.confidence_impact * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditTrail;
