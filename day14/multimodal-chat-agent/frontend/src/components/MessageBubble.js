import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

function MessageBubble({ message }) {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`message-bubble ${message.type} ${message.isError ? 'error' : ''}`}>
      <div className="message-header">
        <span className="message-sender">
          {message.type === 'user' ? '👤 You' : '🤖 Assistant'}
        </span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>
      
      {message.file && (
        <div className="message-file">
          📎 {message.file.name} ({message.file.type})
        </div>
      )}
      
      <div className="message-content">
        <ReactMarkdown
          components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneLight}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
      
      {message.metadata && (
        <div className="message-metadata">
          <small>
            Tokens: {message.metadata.tokens_used} | 
            Model: {message.metadata.model_used}
          </small>
        </div>
      )}
    </div>
  );
}

export default MessageBubble;
