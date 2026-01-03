import React, { useEffect, useState } from 'react';
import { MessageSquare, Plus } from 'lucide-react';
import type { UserConversation } from '../../types/chat';
import './Sidebar.css';

interface SidebarProps {
    userId: string;
    onSelectConversation: (conversationId: string) => void;
    onNewChat: () => void;
    currentConversationId: string | null;
    lastUpdated?: number;
}

const API_BASE_URL = 'http://localhost:8080';

export const Sidebar: React.FC<SidebarProps> = ({
    userId,
    onSelectConversation,
    onNewChat,
    currentConversationId,
    lastUpdated
}) => {
    const [conversations, setConversations] = useState<UserConversation[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const fetchConversations = async () => {
            if (!userId || userId === 'anonymous') return;

            setIsLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/users/${userId}/conversations`);
                if (response.ok) {
                    const data = await response.json();
                    setConversations(data);
                }
            } catch (error) {
                console.error("Error fetching conversations:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchConversations();
    }, [userId, currentConversationId, lastUpdated]); // Refresh when conversation changes or lastUpdated trigger

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <button className="new-chat-btn" onClick={onNewChat}>
                    <Plus size={18} />
                    <span>Nuevo Chat</span>
                </button>
            </div>

            <div className="conversations-list">
                <div className="list-title">Historial Reciente</div>

                {isLoading && <div className="loading-indicator">Cargando...</div>}

                {!isLoading && conversations.length === 0 && (
                    <div className="empty-state">No hay conversaciones previas</div>
                )}

                {conversations.map((conv) => (
                    <div
                        key={conv.conversation_id}
                        className={`conversation-item ${currentConversationId === conv.conversation_id ? 'active' : ''}`}
                        onClick={() => onSelectConversation(conv.conversation_id)}
                    >
                        <MessageSquare size={16} className="conv-icon" />
                        <div className="conv-details">
                            <span className="conv-date">{formatDate(conv.conversation_created_at)}</span>
                            <span className="conv-id">ID: {conv.conversation_id.substring(0, 8)}...</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
