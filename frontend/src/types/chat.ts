export interface Message {
    role: 'user' | 'agent';
    type: string;
    content: string;
    timestamp: string;
    // For visual representation of "images" sent by user
    attachments?: string[];
    // For charts sent by the agent
    charts?: any[];
}

export interface ChartData {
    data: any[];
    layout: any;
}

export interface ChatResponse {
    response: string;
    conversation_id: string;
    queries_executed: any[];
    plotly_charts: any[];
}

export interface ChatState {
    conversationId: string | null;
    messages: Message[];
    isLoading: boolean;
    input: string;
}
