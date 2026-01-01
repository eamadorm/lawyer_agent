import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types/chat';
import liaIcon from '../../assets/lia_icon_gold.png';
import userIcon from '../../assets/user_icon.png';
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
                {isAgent ? (
                    <img
                        src={liaIcon}
                        alt="LIA"
                        style={{
                            width: '36px',
                            height: '36px',
                            objectFit: 'contain'
                        }}
                    />
                ) : (
                    <img
                        src={userIcon}
                        alt="User"
                        style={{
                            width: '53px',
                            height: '53px',
                            objectFit: 'contain'
                        }}
                    />
                )}
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
