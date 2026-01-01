import React, { useState } from 'react';
import { MainLayout } from '../Layout/MainLayout';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import type { Message } from '../../types/chat';

export const ChatWindow: React.FC = () => {
    const [conversationId, setConversationId] = useState<string | null>(null);

    // Initialize messages from localStorage if available
    const [messages, setMessages] = useState<Message[]>([]);

    const [isLoading, setIsLoading] = useState(false);

    // We removed the backend fetch for history because the backend endpoint 
    // GET /conversations/{id} reads from an in-memory store that is NOT 
    // connected to the BigQuery table used by the chat endpoint. 
    // Therefore, it always returns 404. We rely on client-side persistence instead.


    const handleSendMessage = async (text: string, attachments: string[]) => {
        // 1. Add User Message to UI
        const newUserMsg: Message = {
            role: 'user',
            type: 'text',
            content: text,
            timestamp: new Date().toISOString(),
            attachments: attachments
        };

        setMessages(prev => [...prev, newUserMsg]);
        setIsLoading(true);

        try {
            // 2. Call API
            const response = await fetch('https://lawyer-agent-api-214571216460.us-central1.run.app/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();

            // 3. Update Conversation ID if new
            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
            }


            // 5. Add Agent Response to UI
            const newAgentMsg: Message = {
                role: 'agent',
                type: 'text',
                content: data.response,
                charts: data.plotly_charts, // Still storing in message for history if needed, but display is separate
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, newAgentMsg]);

        } catch (error) {
            console.error(error);
            const errorMsg: Message = {
                role: 'agent',
                type: 'error',
                content: "Sorry, I encountered an error connecting to the server.",
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <MainLayout>
            <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
                {/* Chat Panel - Full Screen */}
                <div style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: 'transparent', // Transparent so watermark shows if we have one
                    // Center the content max-width for better reading experience on large screens?
                    // Or full width as requested. User asked: "ocupe toda la pantalla".
                    // Let's make it full width but maybe constrain the message list inside MessageList component if needed.
                    // For now, full width container.
                    height: '100%',
                    width: '100%'
                }}>
                    <header style={{
                        padding: '1rem',
                        borderBottom: '1px solid rgba(0,0,0,0.1)',
                        background: 'var(--bg-panel)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        boxShadow: 'var(--shadow-sm)'
                    }}>
                        <h2 style={{ margin: 0, color: 'var(--color-primary)', fontSize: '1.25rem' }}>ALIA: Asistente Legal de Investigación Avanzada</h2>
                        {conversationId && (
                            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                                ID: {conversationId.substring(0, 8)}...
                            </span>
                        )}
                    </header>

                    <MessageList messages={messages} isLoading={isLoading} />
                    <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
                </div>
            </div>
        </MainLayout>
    );
};
