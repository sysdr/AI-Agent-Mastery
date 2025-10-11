import React, { useState, useRef, useEffect } from 'react';
import { Send, ThumbsUp, ThumbsDown, HelpCircle } from 'lucide-react';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/api/agent/chat?message=${encodeURIComponent(inputMessage)}&user_id=demo_user`
      );
      
      const data = await response.json();
      
      const agentMessage = {
        id: data.response_id || Date.now() + 1,
        text: data.response,
        sender: 'agent',
        timestamp: new Date(),
        responseId: data.response_id
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'agent',
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (messageId, satisfaction) => {
    const message = messages.find(m => m.id === messageId);
    if (!message || !message.responseId) return;

    try {
      await fetch('http://localhost:8000/api/learning/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'demo_user',
          agent_response_id: message.responseId,
          satisfaction_score: satisfaction,
          demographic_data: {
            age_group: '25-34',
            user_type: 'demo',
            location: 'demo_location'
          }
        })
      });

      // Update message to show feedback was submitted
      setMessages(prev => prev.map(m => 
        m.id === messageId 
          ? { ...m, feedbackSubmitted: satisfaction }
          : m
      ));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const explainDecision = async (messageId) => {
    const message = messages.find(m => m.id === messageId);
    if (!message) return;

    try {
      const response = await fetch('http://localhost:8000/api/learning/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_data: {
            user_message: messages.find(m => m.id === messageId - 1)?.text || '',
            response: message.text,
            user_type: 'demo'
          }
        })
      });
      
      const data = await response.json();
      setExplanation(data.explanation);
    } catch (error) {
      console.error('Failed to get explanation:', error);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="bg-white rounded-lg shadow-md flex-1 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            AI Agent with Production Learning
          </h2>
          <p className="text-sm text-gray-600">
            Chat responses are analyzed for bias and used for continuous learning
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">
                Start a conversation to see production learning in action!
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Your feedback helps improve the AI agent through online learning
              </p>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id} className={`flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.error
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <p className="text-sm">{message.text}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
                
                {/* Feedback buttons for agent messages */}
                {message.sender === 'agent' && !message.error && (
                  <div className="flex items-center space-x-2 mt-2">
                    <button
                      onClick={() => submitFeedback(message.id, 1.0)}
                      disabled={message.feedbackSubmitted !== undefined}
                      className={`p-1 rounded transition-colors ${
                        message.feedbackSubmitted === 1.0
                          ? 'bg-green-200 text-green-800'
                          : 'hover:bg-green-100 text-gray-600'
                      }`}
                      title="Good response"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      onClick={() => submitFeedback(message.id, 0.0)}
                      disabled={message.feedbackSubmitted !== undefined}
                      className={`p-1 rounded transition-colors ${
                        message.feedbackSubmitted === 0.0
                          ? 'bg-red-200 text-red-800'
                          : 'hover:bg-red-100 text-gray-600'
                      }`}
                      title="Poor response"
                    >
                      <ThumbsDown size={14} />
                    </button>
                    <button
                      onClick={() => explainDecision(message.id)}
                      className="p-1 rounded hover:bg-blue-100 text-gray-600"
                      title="Explain this response"
                    >
                      <HelpCircle size={14} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !inputMessage.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Explanation Modal */}
      {explanation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Decision Explanation
            </h3>
            <div className="space-y-3">
              <p className="text-sm text-gray-700">
                {explanation.explanation}
              </p>
              <div className="space-y-2">
                <h4 className="font-medium text-gray-800">Key Factors:</h4>
                {explanation.decision_factors?.map((factor, index) => (
                  <div key={index} className="text-sm">
                    <span className="font-medium">{factor.factor}:</span>
                    <span className="text-gray-600 ml-1">{factor.description}</span>
                  </div>
                ))}
              </div>
              <div className="text-sm text-gray-500">
                Confidence: {Math.round((explanation.confidence_score || 0) * 100)}%
              </div>
            </div>
            <button
              onClick={() => setExplanation(null)}
              className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 w-full"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
