import React, { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import { Send, Image as ImageIcon, X } from 'lucide-react';
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

    return (
        <div className="input-area-container">
            {files.length > 0 && (
                <div className="attachment-preview-bar">
                    {files.map((file, idx) => (
                        <div key={idx} className="preview-item file-preview">
                            <span className="file-icon">📄</span>
                            <span className="file-name">{file.name}</span>
                            <button className="remove-btn" onClick={() => removeAttachment(idx)}>
                                <X size={14} />
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
