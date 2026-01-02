import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Image as ImageIcon, Film, File } from 'lucide-react';
import type { Message } from '../../types/chat';
import liaIcon from '../../assets/lia_icon_gold.png';
import userIcon from '../../assets/user_icon.png';
import './MessageBubble.css';

interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isAgent = message.role === 'agent';

    const getFileIcon = (fileName: string) => {
        const ext = fileName.split('.').pop()?.toLowerCase();

        if (['jpg', 'jpeg', 'png', 'webp', 'svg'].includes(ext || '')) {
            return <ImageIcon size={16} />;
        }
        if (['mp4', 'mp3', 'wav', 'mov', 'avi'].includes(ext || '')) {
            return <Film size={16} />;
        }
        if (['pdf', 'txt', 'md', 'doc', 'docx', 'xls', 'xlsx', 'csv'].includes(ext || '')) {
            return <FileText size={16} />;
        }
        return <File size={16} />;
    };

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
                        <div className="attachments" style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '8px',
                            marginBottom: '12px'
                        }}>
                            {message.attachments.map((fileName, idx) => (
                                <div key={idx} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    backgroundColor: isAgent ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
                                    padding: '6px 10px',
                                    borderRadius: '6px',
                                    border: isAgent ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.1)',
                                    fontSize: '0.85rem',
                                    color: isAgent ? '#f1f5f9' : '#1e293b', // Agent (Dark BG) -> Light Text; User (Light BG) -> Dark Text
                                    maxWidth: '100%'
                                }} title={fileName}>
                                    <span style={{ opacity: 0.8 }}>{getFileIcon(fileName)}</span>
                                    <span style={{
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                        maxWidth: '180px',
                                        fontWeight: 500
                                    }}>
                                        {fileName}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                    {renderContent()}
                </div>
            </div>
        </div>
    );
};
