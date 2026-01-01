import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot } from 'lucide-react';
import type { Message } from '../../types/chat';
import './MessageBubble.css';

interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isAgent = message.role === 'agent';

    // Helper to detect if content is a chart (structure based on backend response)
    const renderContent = () => {
        return (
            <div className="markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
        );
    };

    return (
        <div className={`message-container ${isAgent ? 'agent' : 'user'}`}>
            <div className="avatar">
                {isAgent ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="message-content">
                <div className="bubble">
                    {message.attachments && message.attachments.length > 0 && (
                        <div className="attachments">
                            {message.attachments.map((url, idx) => (
                                <img key={idx} src={url} alt="att" className="attachment-preview" />
                            ))}
                        </div>
                    )}
                    {renderContent()}
                </div>
            </div>
        </div>
    );
};
