import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './app.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ChatMessage = ({ message, isUser, agentType, charts }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-animation`}>
      <div className={`max-w-3xl p-4 rounded-lg ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-100 text-gray-800'
      }`}>
        {!isUser && agentType && (
          <div className="text-xs uppercase font-semibold mb-2 opacity-70">
            {agentType.replace('_', ' ')} Agent
          </div>
        )}
        <div className="whitespace-pre-wrap">{message}</div>
        
        {/* Display charts if available */}
        {charts && Object.keys(charts).length > 0 && (
          <div className="mt-4">
            {Object.entries(charts).map(([key, chartData]) => (
              <div key={key} className="mb-4">
                <img 
                  src={chartData} 
                  alt={`Chart ${key}`}
                  className="max-w-full h-auto rounded-lg shadow-lg"
                  style={{ maxHeight: '500px' }}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const AgentSelector = ({ selectedAgent, onAgentChange }) => {
  const agents = [
    { value: 'manager', label: '👔 Manager Agent' },
    { value: 'sales', label: '💼 Sales Agent' },
    { value: 'analytics', label: '📊 Analytics Agent' },
    { value: 'support', label: '🛠️ Support Agent' },
    { value: 'lead_qualification', label: '🎯 Lead Qualification Agent' },
    { value: 'customer_management', label: '👥 Customer Management Agent' }
  ];

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Select AI Agent:
      </label>
      <select 
        value={selectedAgent}
        onChange={(e) => onAgentChange(e.target.value)}
        className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {agents.map(agent => (
          <option key={agent.value} value={agent.value}>
            {agent.label}
          </option>
        ))}
      </select>
    </div>
  );
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('manager');
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [stats, setStats] = useState({
    salespersons: 0,
    dealers: 0,
    meetings: 0,
    leads: 0
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const endpoints = ['salespersons', 'dealers', 'meetings', 'leads'];
      const requests = endpoints.map(endpoint => 
        axios.get(`${API}/api/${endpoint}`).catch(() => ({ data: [] }))
      );
      
      const responses = await Promise.all(requests);
      setStats({
        salespersons: responses[0].data.length,
        dealers: responses[1].data.length,
        meetings: responses[2].data.length,
        leads: responses[3].data.length
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      content: inputValue,
      isUser: true,
      agentType: selectedAgent
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API}/api/chat`, {
        message: inputValue,
        agent_type: selectedAgent,
        session_id: sessionId
      });

      // Handle charts from response (for analytics agent)
      let charts = null;
      if (response.data.charts && response.data.charts.length > 0) {
        // Convert array of chart base64 strings to object format expected by frontend
        charts = {};
        response.data.charts.forEach((chart, index) => {
          charts[`chart_${index + 1}`] = chart;
        });
      }

      const botMessage = {
        content: response.data.response,
        isUser: false,
        agentType: response.data.agent_type,
        charts: charts
      };

      setMessages(prev => [...prev, botMessage]);
      setInputValue('');
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        content: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        agentType: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleQuickAction = (query, agent) => {
    setSelectedAgent(agent);
    setInputValue(query);
    setTimeout(() => sendMessage(), 100);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Sales Agent Chatbot</h1>
              <span className="ml-3 px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                AI-Powered
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Session: {sessionId}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Salespersons</span>
                  <span className="font-semibold text-blue-600">{stats.salespersons}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Dealers</span>
                  <span className="font-semibold text-green-600">{stats.dealers}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Meetings</span>
                  <span className="font-semibold text-purple-600">{stats.meetings}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Leads</span>
                  <span className="font-semibold text-orange-600">{stats.leads}</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <button
                  onClick={() => handleQuickAction('Show me revenue performance by salesperson with charts', 'analytics')}
                  className="w-full text-left p-3 text-sm bg-blue-50 hover:bg-blue-100 rounded transition-colors"
                >
                  📊 Revenue Analytics
                </button>
                <button
                  onClick={() => handleQuickAction('Show me team performance overview', 'sales')}
                  className="w-full text-left p-3 text-sm bg-green-50 hover:bg-green-100 rounded transition-colors"
                >
                  💼 Team Performance
                </button>
                <button
                  onClick={() => handleQuickAction('Show me lead qualification metrics', 'lead_qualification')}
                  className="w-full text-left p-3 text-sm bg-purple-50 hover:bg-purple-100 rounded transition-colors"
                >
                  🎯 Lead Analytics
                </button>
                <button
                  onClick={() => handleQuickAction('Help me understand the system features', 'support')}
                  className="w-full text-left p-3 text-sm bg-orange-50 hover:bg-orange-100 rounded transition-colors"
                >
                  🛠️ System Help
                </button>
              </div>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow">
              {/* Agent Selector */}
              <div className="p-6 border-b">
                <AgentSelector 
                  selectedAgent={selectedAgent} 
                  onAgentChange={setSelectedAgent} 
                />
              </div>

              {/* Messages */}
              <div className="h-96 overflow-y-auto p-6" style={{ minHeight: '600px' }}>
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 mt-8">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-lg font-medium mb-2">Welcome to Sales Agent Chatbot</h3>
                    <p className="text-sm">
                      Select an agent and start asking questions about your sales data, 
                      performance metrics, or system features.
                    </p>
                  </div>
                )}
                
                {messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    message={message.content}
                    isUser={message.isUser}
                    agentType={message.agentType}
                    charts={message.charts}
                  />
                ))}
                
                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-100 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span className="text-gray-600">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t p-6">
                <div className="flex space-x-4">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Ask the ${selectedAgent.replace('_', ' ')} Agent...`}
                    className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    rows="2"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Send
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Press Enter to send, Shift+Enter for new line
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;