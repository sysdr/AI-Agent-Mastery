import React from 'react';
import { PlusIcon, ChatBubbleLeftIcon, UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const Sidebar = ({ 
  conversations, 
  selectedConversation, 
  onSelectConversation, 
  onNewConversation, 
  user, 
  onLogout 
}) => {
  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Conversation
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-2">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
              className={`p-3 rounded-lg cursor-pointer transition-colors ${
                selectedConversation === conversation.id
                  ? 'bg-indigo-50 border border-indigo-200'
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start space-x-3">
                <ChatBubbleLeftIcon className="h-5 w-5 text-gray-400 mt-1" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {format(new Date(conversation.created_at), 'MMM d, yyyy')}
                  </p>
                  {conversation.messages.length > 0 && (
                    <p className="text-xs text-gray-400 mt-1 truncate">
                      {conversation.messages[conversation.messages.length - 1].content.substring(0, 50)}...
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3">
          <UserCircleIcon className="h-8 w-8 text-gray-400" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name || 'Demo User'}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user?.tenant_id || 'tenant_1'}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="p-1 text-gray-400 hover:text-gray-500"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
