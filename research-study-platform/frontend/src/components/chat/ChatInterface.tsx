import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { chatApi } from '../../services/api';
import { ChatInteraction, ChatSession, CostLimits } from '../../types';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  PaperAirplaneIcon, 
  ExclamationTriangleIcon,
  CpuChipIcon,
  BanknotesIcon,
  ClockIcon,
  CommandLineIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

interface ChatInterfaceProps {
  sessionId: string;
  onSessionUpdate?: (session: ChatSession) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, onSessionUpdate }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatInteraction[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationTurn, setConversationTurn] = useState(1);
  const [chatSession, setChatSession] = useState<ChatSession | null>(null);
  const [costLimits, setCostLimits] = useState<CostLimits | null>(null);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeChatSession();
    fetchCostLimits();
  }, [sessionId]);

  const initializeChatSession = async () => {
    try {
      setIsLoading(true);
      const response = await chatApi.startSession(sessionId);
      setChatSession(response.data);
      setSessionStarted(true);
      
      // Load existing messages
      const historyResponse = await chatApi.getHistory(sessionId);
      setMessages(historyResponse.data);
      
      // Set conversation turn based on existing messages
      const maxTurn = Math.max(0, ...historyResponse.data.map(msg => msg.conversation_turn));
      setConversationTurn(maxTurn + 1);
      
      onSessionUpdate?.(response.data);
    } catch (error: any) {
      toast.error('Failed to initialize chat session');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCostLimits = async () => {
    try {
      const response = await chatApi.getCostLimits();
      setCostLimits(response.data);
    } catch (error) {
      console.error('Failed to fetch cost limits:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const messageText = currentMessage.trim();
    setCurrentMessage('');
    setIsTyping(true);

    try {
      const response = await chatApi.sendMessage({
        message: messageText,
        session_id: sessionId,
        conversation_turn: conversationTurn
      });

      // Add user message to display
      const userInteraction: ChatInteraction = {
        id: `user-${Date.now()}`,
        session: sessionId,
        user: user?.id || '',
        message_type: 'user',
        conversation_turn: conversationTurn,
        user_message: messageText,
        assistant_response: undefined,
        error_message: undefined,
        response_time_ms: undefined,
        total_tokens: undefined,
        estimated_cost_usd: undefined,
        contains_linux_command: false,
        rate_limit_hit: false,
        message_timestamp: new Date().toISOString()
      };

      // Add assistant response to display
      const assistantInteraction: ChatInteraction = {
        id: response.data.interaction_id,
        session: sessionId,
        user: user?.id || '',
        message_type: 'assistant',
        conversation_turn: conversationTurn,
        user_message: undefined,
        assistant_response: response.data.assistant_response,
        error_message: undefined,
        response_time_ms: response.data.response_time_ms,
        total_tokens: response.data.total_tokens,
        estimated_cost_usd: undefined,
        contains_linux_command: false,
        rate_limit_hit: false,
        message_timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userInteraction, assistantInteraction]);
      setConversationTurn(prev => prev + 1);

      // Refresh cost limits
      fetchCostLimits();

    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to send message');
      
      // Show cost limit error if applicable
      if (error.response?.status === 429) {
        toast.error('Daily or weekly cost limit reached. Please try again later.');
      }
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatCost = (cost: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 4
    }).format(cost);
  };

  if (!sessionStarted) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Linux commands data
  const linuxCommands = [
    { cmd: 'ls', desc: 'List files and directories' },
    { cmd: 'cd', desc: 'Change directory' },
    { cmd: 'pwd', desc: 'Print working directory' },
    { cmd: 'cat', desc: 'Display file contents' },
    { cmd: 'cp', desc: 'Copy files/directories' },
    { cmd: 'mv', desc: 'Move/rename files' },
    { cmd: 'chmod', desc: 'Change file permissions' },
    { cmd: 'chown', desc: 'Change file ownership' },
    { cmd: 'grep', desc: 'Search text patterns' },
    { cmd: 'find', desc: 'Search files/directories' }
  ];

  const handleCommandClick = (command: string) => {
    setCurrentMessage(`How does the ${command} command work?`);
  };

  return (
    <div className="flex h-full bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Linux Commands Sidebar */}
      <div className={`${showSidebar ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-200 bg-gray-50`}>
        <div className="p-4 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900 flex items-center">
              <CommandLineIcon className="h-5 w-5 mr-2 text-blue-600" />
              Linux Commands
            </h3>
            <button
              onClick={() => setShowSidebar(false)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <ChevronLeftIcon className="h-4 w-4" />
            </button>
          </div>
          
          <div className="space-y-2 flex-1 overflow-y-auto">
            {linuxCommands.map((item) => (
              <button
                key={item.cmd}
                onClick={() => handleCommandClick(item.cmd)}
                className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors group"
              >
                <div className="font-mono text-sm font-semibold text-blue-600 group-hover:text-blue-700">
                  {item.cmd}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {item.desc}
                </div>
              </button>
            ))}
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-800 font-medium mb-1">💡 Quick Start</p>
            <p className="text-xs text-blue-700">
              Click any command above to ask about it, or type your own questions!
            </p>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          {!showSidebar && (
            <button
              onClick={() => setShowSidebar(true)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 mr-2"
            >
              <ChevronRightIcon className="h-5 w-5" />
            </button>
          )}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <CpuChipIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Linux Learning Assistant</h3>
            <p className="text-sm text-gray-600">
              Ask questions about the 10 Linux commands
            </p>
          </div>
        </div>
        
        {/* Cost and Usage Info */}
        <div className="flex items-center space-x-4 text-sm">
          {chatSession && (
            <div className="flex items-center space-x-2 text-gray-600">
              <ClockIcon className="h-4 w-4" />
              <span>{chatSession.total_messages} messages</span>
            </div>
          )}
          
          {costLimits && (
            <div className="flex items-center space-x-2 text-gray-600">
              <BanknotesIcon className="h-4 w-4" />
              <span>
                {formatCost(costLimits.daily_cost)} / {formatCost(costLimits.daily_cost + costLimits.daily_remaining)}
              </span>
            </div>
          )}
          </div>
        </div>

        {/* Cost Limit Warning */}
      {costLimits && (costLimits.daily_limit_exceeded || costLimits.weekly_limit_exceeded) && (
        <div className="p-4 bg-red-50 border-b border-red-200">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-red-800">
                Cost limit reached
              </p>
              <p className="text-sm text-red-700">
                {costLimits.daily_limit_exceeded 
                  ? 'Daily cost limit exceeded. Please try again tomorrow.'
                  : 'Weekly cost limit exceeded. Please try again next week.'}
              </p>
            </div>
          </div>
          </div>
        )}

        {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CpuChipIcon className="h-6 w-6 text-blue-600" />
            </div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to the Linux Learning Assistant
            </h4>
            <p className="text-gray-600 mb-4">
              I'm here to help you learn Linux commands! {!showSidebar && 'Click the arrow on the left to see the commands, or'} Ask me anything about the 10 Linux commands.
            </p>
            <div className="text-sm text-gray-500">
              💬 Try asking: "How does the ls command work?" or "What's the difference between cp and mv?"
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.message_type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.message_type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">
                {message.user_message || message.assistant_response}
              </p>
              
              {message.message_type === 'assistant' && (
                <div className="mt-2 text-xs text-gray-500 flex items-center space-x-2">
                  {message.response_time_ms && (
                    <span>{message.response_time_ms}ms</span>
                  )}
                  {message.total_tokens && (
                    <span>{message.total_tokens} tokens</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-1">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-xs text-gray-500 ml-2">Assistant is typing...</span>
              </div>
            </div>
          </div>
        )}
        
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
      <div className="p-4 border-t">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={showSidebar ? "Ask about any Linux command..." : "Ask about Linux commands (click → to see command list)..."}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={1}
              disabled={isLoading || (costLimits?.daily_limit_exceeded || costLimits?.weekly_limit_exceeded)}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading || (costLimits?.daily_limit_exceeded || costLimits?.weekly_limit_exceeded)}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <LoadingSpinner size="sm" />
            ) : (
              <PaperAirplaneIcon className="h-5 w-5" />
            )}
          </button>
        </div>
        
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>Press Enter to send{showSidebar ? ', or click commands on the left' : ', Shift+Enter for new line'}</span>
          {costLimits && (
            <span>
              Daily remaining: {formatCost(costLimits.daily_remaining)}
            </span>
          )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;