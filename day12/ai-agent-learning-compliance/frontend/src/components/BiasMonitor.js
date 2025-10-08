import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const BiasMonitor = () => {
  const [biasReport, setBiasReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBiasReport();
  }, []);

  const fetchBiasReport = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/bias-report`);
      setBiasReport(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch bias report:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading bias report...</div>;

  return (
    <div className="bias-monitor">
      <h2>Bias Detection Report</h2>
      
      <div className="bias-summary">
        <div className={`bias-score ${biasReport?.has_significant_bias ? 'warning' : 'ok'}`}>
          Overall Bias Score: {biasReport?.overall_bias_score?.toFixed(3) || '0.000'}
        </div>
        
        {biasReport?.has_significant_bias && (
          <div className="bias-alert">
            <strong>⚠️ Significant bias detected!</strong>
            <p>Affected users: {biasReport.affected_user_count}</p>
          </div>
        )}
      </div>

      <div className="bias-metrics">
        <h3>Bias Metrics</h3>
        {biasReport?.bias_metrics?.length > 0 ? (
          biasReport.bias_metrics.map((metric, index) => (
            <div key={index} className="metric-item">
              <div className="metric-name">{metric.metric_name}</div>
              <div className="metric-value">{metric.value.toFixed(3)}</div>
              <div className="metric-status">
                {metric.is_significant ? '❌ Significant' : '✅ Within threshold'}
              </div>
            </div>
          ))
        ) : (
          <p>No bias metrics available</p>
        )}
      </div>

      <div className="recommendations">
        <h3>Recommendations</h3>
        {biasReport?.recommendations?.map((rec, index) => (
          <div key={index} className="recommendation">
            {rec}
          </div>
        ))}
      </div>
    </div>
  );
};

export default BiasMonitor;
