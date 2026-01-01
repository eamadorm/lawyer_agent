import React, { useState } from 'react';
import { MainLayout } from '../Layout/MainLayout';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import type { Message } from '../../types/chat';
import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const ChatWindow: React.FC = () => {
    const navigate = useNavigate();
    const [conversationId, setConversationId] = useState<string | null>(null);

    // Initialize messages from localStorage if available
    const [messages, setMessages] = useState<Message[]>([]);

    const [isLoading, setIsLoading] = useState(false);
    const userId = localStorage.getItem('user_id') || 'anonymous';

    // Initial Welcome Message (Static)
    React.useEffect(() => {
        const welcomeMsg: Message = {
            role: 'agent',
            type: 'text',
            content: "¡Hola! Soy LIA (Asistente Legal de Investigación Avanzada).\n\nEstoy aquí para ayudarte a navegar el marco legal mexicano con información precisa y verificada.\n\n¿En qué puedo ayudarte hoy?",
            timestamp: new Date().toISOString()
        };
        setMessages([welcomeMsg]);
    }, []);


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
                    user_id: userId,
                    // Use conversational ID if we have it from previous USER interactions, otherwise null
                    conversation_id: conversationId
                })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();

            // 3. Update Conversation ID if new (Only for user-initiated threads)
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

    const handleLogout = () => {
        localStorage.removeItem('user_id');
        navigate('/');
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
                        borderBottom: '1px solid rgba(56, 189, 248, 0.2)', // Light blue border
                        background: '#0f172a', // Dark Slate/Navy (matches login)
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)'
                    }}>
                        <h2 style={{
                            margin: 0,
                            color: 'white',
                            fontSize: '1.1rem', // Reduced from 1.25rem
                            fontFamily: "'Montserrat', sans-serif",
                            fontStyle: 'italic',
                            fontWeight: 400, // Removed bold
                            letterSpacing: '0.05em'
                        }}>LIA: Asistente Legal de Investigación Avanzada</h2>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            {conversationId && (
                                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                                    ID: {conversationId.substring(0, 8)}...
                                </span>
                            )}
                            <button
                                onClick={handleLogout}
                                style={{
                                    background: 'transparent',
                                    border: '1px solid #334155',
                                    color: '#cbd5e1',
                                    cursor: 'pointer',
                                    padding: '0.4rem',
                                    borderRadius: '0.375rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 0.2s'
                                }}
                                title="Cerrar Sesión"
                                onMouseOver={(e) => {
                                    e.currentTarget.style.borderColor = '#ef4444';
                                    e.currentTarget.style.color = '#ef4444';
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.borderColor = '#334155';
                                    e.currentTarget.style.color = '#cbd5e1';
                                }}
                            >
                                <LogOut size={16} />
                            </button>
                        </div>
                    </header>

                    <MessageList messages={messages} isLoading={isLoading} />
                    <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
                </div>
            </div>
        </MainLayout>
    );
};
