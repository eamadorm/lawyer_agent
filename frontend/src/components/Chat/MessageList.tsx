import React, { useEffect, useRef } from 'react';
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
                    <span>Thinking...</span>
                    <div className="dots">
                        <span>.</span><span>.</span><span>.</span>
                    </div>
                </div>
            )}

            <div ref={bottomRef} />
        </div>
    );
};
