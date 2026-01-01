import React, { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import { Send, Image as ImageIcon, X } from 'lucide-react';
import { Button } from '../UI/Button';
import './InputArea.css';

interface InputAreaProps {
    onSendMessage: (text: string, attachments: string[]) => void;
    isLoading: boolean;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSendMessage, isLoading }) => {
    const [input, setInput] = useState('');
    const [attachments, setAttachments] = useState<string[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if ((!input.trim() && attachments.length === 0) || isLoading) return;
        onSendMessage(input, attachments);
        setInput('');
        setAttachments([]);

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

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const imageUrl = URL.createObjectURL(file);
            setAttachments((prev) => [...prev, imageUrl]);

            // Reset input so same file can be selected again if needed
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const removeAttachment = (index: number) => {
        setAttachments((prev) => prev.filter((_, i) => i !== index));
        // Note: In a real app involving object URLs, we should revokeObjectURL to avoid leaks.
    };

    return (
        <div className="input-area-container">
            {attachments.length > 0 && (
                <div className="attachment-preview-bar">
                    {attachments.map((url, idx) => (
                        <div key={idx} className="preview-item">
                            <img src={url} alt="preview" />
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
                    title="Add image"
                    disabled={isLoading}
                >
                    <ImageIcon size={20} />
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept="image/*"
                    onChange={handleFileChange}
                />

                <textarea
                    ref={textareaRef}
                    className="message-input"
                    placeholder="Preguntar a ALIA"
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
                    disabled={(!input.trim() && attachments.length === 0) || isLoading}
                    size="sm"
                >
                    <Send size={18} />
                </Button>
            </div>
        </div>
    );
};
