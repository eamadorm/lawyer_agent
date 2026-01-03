import React, { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import type { Message } from '../../types/chat';
import { MessageBubble } from './MessageBubble';
import './MessageList.css';

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    return (
        <div className="message-list">

            {messages.map((msg, index) => (
                <MessageBubble key={index} message={msg} />
            ))}

            {isLoading && (
                <div className="loading-indicator">
                    <Loader2 className="spinner" size={16} />
                    <span>Pensando...</span>
                </div>
            )}

            <div ref={bottomRef} />
        </div>
    );
};
