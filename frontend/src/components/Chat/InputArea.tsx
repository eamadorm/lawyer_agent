import React, { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import { Send, Image as ImageIcon, X, FileText, Film } from 'lucide-react';
import { Button } from '../UI/Button';
import './InputArea.css';
/* Add simple styles for file preview inside the component if css file is not editable or for quick iteration, 
   but since we are targeting InputArea.tsx we rely on InputArea.css existing. 
   Assuming the user can see visual changes. We will just use inline styles or existing classes.
   The previous replacement used generic classes. */

interface InputAreaProps {
    onSendMessage: (text: string, files: File[]) => void;
    isLoading: boolean;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isLoading }) => {
    const [input, setInput] = useState('');
    const [files, setFiles] = useState<File[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if ((!input.trim() && files.length === 0) || isLoading) return;
        onSendMessage(input, files);
        setInput('');
        setFiles([]);

        // Reset height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Extensions matched with backend
    const ALLOWED_EXTENSIONS = [
        '.pdf', '.txt', '.md', '.html', '.json',
        '.jpg', '.jpeg', '.png', '.webp', '.svg',
        '.mp4', '.mp3', '.wav', '.mov', '.avi'
    ];

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

            if (!ALLOWED_EXTENSIONS.includes(fileExt)) {
                window.alert("This file is not supported / Este archivo no es compatible");
                if (fileInputRef.current) fileInputRef.current.value = '';
                return;
            }

            setFiles((prev) => [...prev, file]);

            // Reset input so same file can be selected again if needed
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const removeAttachment = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
    };

    // Helper for icons (keep consistent with MessageBubble)
    const getFileIcon = (fileName: string) => {
        const ext = fileName.split('.').pop()?.toLowerCase();

        if (['jpg', 'jpeg', 'png', 'webp', 'svg'].includes(ext || '')) {
            return <ImageIcon size={20} color="#cbd5e1" />;
        }
        if (['mp4', 'mp3', 'wav', 'mov', 'avi'].includes(ext || '')) {
            return <Film size={20} color="#cbd5e1" />;
        }
        if (['pdf', 'txt', 'md', 'doc', 'docx', 'xls', 'xlsx', 'csv'].includes(ext || '')) {
            return <FileText size={20} color="#cbd5e1" />;
        }
        return <FileText size={20} color="#cbd5e1" />;
    };

    return (
        <div className="input-area-container">
            {files.length > 0 && (
                <div className="attachment-preview-bar" style={{
                    display: 'flex',
                    gap: '12px',
                    marginBottom: '10px',
                    overflowX: 'auto',
                    paddingBottom: '4px'
                }}>
                    {files.map((file, idx) => (
                        <div key={idx} className="preview-item file-preview" style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            padding: '8px 12px',
                            borderRadius: '8px',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            position: 'relative',
                            minWidth: 'fit-content'
                        }}>
                            {getFileIcon(file.name)}
                            <span className="file-name" style={{
                                color: '#ffffff', // Explicitly white
                                fontSize: '0.9rem',
                                fontWeight: 500,
                                maxWidth: '200px',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                            }}>{file.name}</span>

                            <button
                                onClick={() => removeAttachment(idx)}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#94a3b8',
                                    cursor: 'pointer',
                                    marginLeft: '4px',
                                    padding: '2px',
                                    display: 'flex',
                                    alignItems: 'center'
                                }}
                                onMouseOver={(e) => e.currentTarget.style.color = '#ef4444'}
                                onMouseOut={(e) => e.currentTarget.style.color = '#94a3b8'}
                            >
                                <X size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="input-row">
                <button
                    className="attach-btn"
                    onClick={() => fileInputRef.current?.click()}
                    title="Adjuntar archivo (PDF, Texto, Imagen, Video...)"
                    disabled={isLoading}
                >
                    <ImageIcon size={20} />
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    // Accept only Vertex AI supported types
                    accept=".pdf,.txt,.md,.html,.json,.jpg,.jpeg,.png,.webp,.svg,.mp4,.mp3,.wav,.mov,.avi"
                    onChange={handleFileChange}
                />

                <textarea
                    ref={textareaRef}
                    className="message-input"
                    placeholder="Preguntar a LIA"
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        e.target.style.height = 'auto';
                        e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
                    }}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                    rows={1}
                    style={{ overflowY: input.length > 50 ? 'auto' : 'hidden' }}
                />

                <Button
                    className="send-btn"
                    onClick={handleSend}
                    disabled={(!input.trim() && files.length === 0) || isLoading}
                    size="sm"
                >
                    <Send size={18} />
                </Button>
            </div>
        </div>
    );
};
