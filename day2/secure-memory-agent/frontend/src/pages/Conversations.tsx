import React, { useState } from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Conversations: React.FC = () => {
  const [newMessage, setNewMessage] = useState('');
  const [currentConversation, setCurrentConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([]);

  const createNewConversation = async () => {
    try {
      const conversation = await apiService.createConversation('demo-user', 'New Conversation');
      setCurrentConversation(conversation.id);
      setMessages([]);
      toast.success('New conversation created');
    } catch (error) {
      toast.error('Failed to create conversation');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !currentConversation) return;

    try {
      const message = await apiService.addMessage({
        content: newMessage,
        role: 'user',
        conversation_id: currentConversation
      });

      setMessages(prev => [...prev, message]);
      setNewMessage('');
      toast.success('Message sent');
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Conversations</h1>
        <button
          onClick={createNewConversation}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {currentConversation ? (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">Conversation {currentConversation.slice(0, 8)}</h2>
          </div>
          
          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p>{message.content}</p>
                  {message.pii_detected && (
                    <div className="mt-1 text-xs opacity-75">
                      ⚠️ PII Detected
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              />
              <button
                onClick={sendMessage}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
          <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No conversation selected</h3>
          <p className="text-gray-500 mb-6">Create a new conversation to start chatting</p>
          <button
            onClick={createNewConversation}
            className="btn btn-primary"
          >
            Start New Conversation
          </button>
        </div>
      )}
    </div>
  );
};

export default Conversations;
