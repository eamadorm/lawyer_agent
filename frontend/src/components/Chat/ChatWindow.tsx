import React, { useState } from 'react';
import { MainLayout } from '../Layout/MainLayout';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { Sidebar } from './Sidebar';
import type { Message, ConversationMessage } from '../../types/chat';
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
    const welcomeMsg: Message = {
        role: 'agent',
        type: 'text',
        content: "¡Hola! Soy LIA (Asistente Legal de Investigación Avanzada).\n\nEstoy aquí para ayudarte a navegar el marco legal mexicano con información precisa y verificada.\n\n¿En qué puedo ayudarte hoy?",
        timestamp: new Date().toISOString()
    };

    React.useEffect(() => {
        // Only set welcome message if no conversation is selected
        if (!conversationId) {
            setMessages([welcomeMsg]);
        }
    }, [conversationId]);


    // const API_BASE_URL = 'https://lawyer-agent-api-214571216460.us-central1.run.app';
    // Use the production Cloud Run URL
    const API_BASE_URL = 'http://localhost:8080'; // 'https://lawyer-agent-api-214571216460.us-central1.run.app';

    const createConversationId = async (): Promise<string> => {
        const response = await fetch(`${API_BASE_URL}/create_conversation_id`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) throw new Error('Failed to create conversation ID');
        const data = await response.json();
        return data.conversation_id;
    };

    const uploadFile = async (file: File, currentConversationId: string): Promise<{ url: string; media_type: string }> => {
        // Force content-type to application/octet-stream to allow any file type 
        // (the file extension is validated by the backend)
        const contentType = 'application/octet-stream';

        // 1. Get Signed URL
        const uploadUrlRes = await fetch(`${API_BASE_URL}/get_gcs_upload_url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: file.name,
                content_type: contentType,
                user_id: userId,
                conversation_id: currentConversationId
            })
        });

        if (!uploadUrlRes.ok) throw new Error('Failed to get upload URL');

        const { upload_url, gcs_uri } = await uploadUrlRes.json();

        // 2. Upload to GCS
        const putRes = await fetch(upload_url, {
            method: 'PUT',
            headers: {
                'Content-Type': contentType
            },
            body: file
        });

        if (!putRes.ok) throw new Error('Failed to upload file to GCS');

        return { url: gcs_uri, media_type: contentType };
    };

    const handleSendMessage = async (text: string, files: File[]) => {
        // 1. Add User Message to UI
        const newUserMsg: Message = {
            role: 'user',
            type: 'text',
            content: text,
            timestamp: new Date().toISOString(),
            attachments: files.map(f => f.name) // Show filenames
        };

        setMessages(prev => [...prev, newUserMsg]);
        setIsLoading(true);

        try {
            // 2. Ensure Conversation ID exists
            let currentConversationId = conversationId;
            if (!currentConversationId) {
                currentConversationId = await createConversationId();
                setConversationId(currentConversationId);
            }

            // 3. Upload Files First (if any)
            const uploadedDocs = [];
            for (const file of files) {
                const doc = await uploadFile(file, currentConversationId);
                // Backend expects list of objects with 'gcs_uri' key
                uploadedDocs.push({ gcs_uri: doc.url });
            }

            // 4. Call Chat API
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    user_id: userId,
                    conversation_id: currentConversationId,
                    documents: uploadedDocs
                })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();

            // 5. Add Agent Response to UI
            const newAgentMsg: Message = {
                role: 'agent',
                type: 'text',
                content: data.response,
                charts: data.plotly_charts,
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

    const handleSelectConversation = async (convId: string) => {
        setConversationId(convId);
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/conversations/${convId}/messages`);
            if (response.ok) {
                const data: ConversationMessage[] = await response.json();

                // Transform backend messages to frontend format
                const uiMessages: Message[] = data.map(msg => ({
                    role: msg.role === 'user' ? 'user' : 'agent',
                    type: 'text',
                    content: msg.content,
                    timestamp: msg.created_at
                }));

                setMessages(uiMessages);
            }
        } catch (error) {
            console.error("Error loading conversation:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewChat = () => {
        setConversationId(null);
        setMessages([welcomeMsg]);
    };

    const handleLogout = () => {
        localStorage.removeItem('user_id');
        navigate('/');
    };

    return (
        <MainLayout>
            <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', position: 'relative' }}>
                <Sidebar
                    userId={userId}
                    onSelectConversation={handleSelectConversation}
                    onNewChat={handleNewChat}
                    currentConversationId={conversationId}
                />
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
