import React from 'react';
import { format } from 'date-fns';
import { UserCircleIcon, CpuChipIcon } from '@heroicons/react/24/outline';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} message-bubble`}>
      <div className={`flex max-w-xs lg:max-w-md ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end space-x-2`}>
        <div className={`flex-shrink-0 ${isUser ? 'ml-2' : 'mr-2'}`}>
          {isUser ? (
            <UserCircleIcon className="h-6 w-6 text-gray-400" />
          ) : (
            <CpuChipIcon className="h-6 w-6 text-indigo-500" />
          )}
        </div>
        
        <div>
          <div className={`px-4 py-2 rounded-lg shadow ${
            isUser 
              ? 'bg-indigo-600 text-white' 
              : 'bg-white text-gray-900'
          }`}>
            <p className="text-sm whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
          
          <p className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {format(new Date(message.timestamp), 'h:mm a')}
          </p>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
