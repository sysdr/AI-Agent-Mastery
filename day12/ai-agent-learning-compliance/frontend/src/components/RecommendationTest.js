import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const RecommendationTest = () => {
  const [userId, setUserId] = useState('test_user_001');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/recommendations/${userId}?count=5`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
    setLoading(false);
  };

  const recordInteraction = async (itemId, interactionType) => {
    try {
      await axios.post(`${API_BASE_URL}/interactions`, {
        user_id: userId,
        item_id: itemId,
        interaction_type: interactionType,
        context: { test_mode: true }
      });
      alert(`Recorded ${interactionType} for ${itemId}`);
    } catch (error) {
      console.error('Failed to record interaction:', error);
    }
  };

  return (
    <div className="recommendation-test">
      <h2>Test Recommendations</h2>
      
      <div className="test-controls">
        <input
          type="text"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <button onClick={fetchRecommendations} disabled={loading}>
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {recommendations && (
        <div className="recommendations-section">
          <h3>Recommendations for {recommendations.user_id}</h3>
          <p>Generated at: {new Date(recommendations.generated_at).toLocaleString()}</p>
          <p>Algorithm: {recommendations.algorithm_version}</p>
          
          {recommendations.recommendations.map((rec, index) => (
            <div key={index} className="recommendation-item">
              <div className="rec-header">
                <strong>{rec.item_id}</strong>
                <span className="recommendation-score">Score: {rec.score.toFixed(2)}</span>
              </div>
              <div className="recommendation-explanation">{rec.explanation}</div>
              <div className="rec-actions">
                <button onClick={() => recordInteraction(rec.item_id, 'view')}>👁️ View</button>
                <button onClick={() => recordInteraction(rec.item_id, 'like')}>👍 Like</button>
                <button onClick={() => recordInteraction(rec.item_id, 'click')}>🖱️ Click</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationTest;
