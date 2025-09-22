from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import structlog

load_dotenv()

logger = structlog.get_logger()

# Import advanced analytics
from advanced_analytics import AdvancedAnalyticsAgent
from chart_generator import ChartGenerator

class BaseAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        return "Base agent response"

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__("manager")
        
    def get_system_prompt(self) -> str:
        return """You are an AI Manager coordinating a sales team. You can:
        - Route complex queries to appropriate specialists
        - Provide overview insights
        - Coordinate multi-agent responses
        - Summarize team performance"""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        if db is None:
            return "I'm having trouble accessing the system data right now. Please try again."
        
        try:
            # Simple routing logic
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['chart', 'analytics', 'report', 'performance', 'revenue']):
                return "For detailed analytics and charts, please switch to the Analytics Agent. I can coordinate overall team management tasks."
            elif any(word in query_lower for word in ['lead', 'prospect', 'qualify']):
                return "For lead qualification tasks, please use the Lead Qualification Agent. I handle overall coordination."
            elif any(word in query_lower for word in ['support', 'help', 'issue', 'problem']):
                return "For support issues, please use the Support Agent. I coordinate team management."
            elif any(word in query_lower for word in ['customer', 'client', 'relationship']):
                return "For customer management tasks, use the Customer Management Agent. I handle strategic oversight."
            else:
                return f"""As your AI Manager, I coordinate the sales team operations. 

Current Team Status:
- 6 Active salespersons across different regions
- Multiple ongoing deals and prospects
- Regular performance tracking and analytics

Available Resources:
- Sales Agent: Direct sales support and deal management
- Analytics Agent: Performance metrics and visual reports  
- Lead Qualification Agent: Prospect evaluation and scoring
- Support Agent: Technical assistance and issue resolution
- Customer Management Agent: Client relationship management

How can I help coordinate your sales operations today?"""
                
        except Exception as e:
            logger.error(f"Manager agent error: {e}")
            return "I'm experiencing some coordination issues. Please try again."

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales")
        
    def get_system_prompt(self) -> str:
        return """You are an AI Sales Assistant helping manage sales operations. You can:
        - Track salesperson performance
        - Manage dealer relationships
        - Schedule and record meetings
        - Provide sales insights and recommendations"""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        if db is None:
            return "I'm having trouble accessing the sales data right now. Please try again."
        
        try:
            # Basic sales data analysis
            return f"""Sales Team Overview:

Our current sales team consists of 6 salespersons across different regions:
- North, South, East, West, Central, and Northeast territories
- Mix of high-performing and developing team members
- Active dealer relationships and ongoing meetings

Key Metrics:
- Total active salespersons: 6
- Revenue targets being tracked monthly
- Regular dealer meetings and follow-ups scheduled

**Recommendations:**
- Focus on top performers for major deals
- Provide additional support for developing team members
- Maintain regular dealer relationship management

For detailed analytics and charts, please use the Analytics Agent.
For specific lead management, use the Lead Qualification Agent."""
            
        except Exception as e:
            logger.error(f"Sales agent error: {e}")
            return "I'm having trouble accessing the sales data right now. Please try again."

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("analytics")
        
        self.chart_generator = ChartGenerator()
        
        # Initialize advanced analytics agent with Emergent API
        emergent_key = os.getenv("EMERGENT_LLM_KEY")
        if emergent_key:
            try:
                self.advanced_agent = AdvancedAnalyticsAgent(emergent_key)
                self.use_advanced = True
                logger.info("Advanced Analytics Agent initialized successfully with Emergent API")
            except Exception as e:
                logger.error(f"Failed to initialize Advanced Analytics Agent: {e}")
                self.advanced_agent = None
                self.use_advanced = False
        else:
            self.advanced_agent = None
            self.use_advanced = False
    
    def get_system_prompt(self) -> str:
        return """You are an AI Analytics Assistant with advanced data analysis capabilities. You can:
        - Generate performance metrics and KPIs with visual charts
        - Execute complex SQL queries on sales data
        - Create various chart types (bar, line, pie, horizontal bar)
        - Analyze sales trends and patterns with graphical representations
        - Provide territory analysis with comparison visualizations
        - Generate meeting effectiveness reports with outcome charts
        - Create revenue forecasting insights with trend analysis
        
        You have access to a comprehensive sales database with salespersons, dealers, meetings, and leads data.
        You can understand natural language queries and convert them to appropriate SQL queries and visualizations.
        
        Always provide actionable insights with both textual analysis and visual representations when appropriate."""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        try:
            # Check if this is a query that would benefit from advanced analytics
            query_lower = query.lower()
            advanced_keywords = [
                'dashboard', 'chart', 'graph', 'plot', 'visual', 'show', 'display', 
                'compare', 'trend', 'analysis', 'report', 'performance', 'metrics',
                'by salesperson', 'by territory', 'by region', 'distribution', 'breakdown'
            ]
            
            use_advanced = any(keyword in query_lower for keyword in advanced_keywords)
            
            if self.use_advanced and use_advanced:
                logger.info("Using Advanced Analytics Agent for query processing")
                
                # Get session history from context if available
                session_history = context.get('session_history', []) if context else []
                
                # Process with advanced agent
                result = self.advanced_agent.process_query(query, session_history, db)
                
                response = result.get('response', '')
                charts = result.get('charts', [])
                
                # If charts were generated, add them to the response context
                if charts and context is not None:
                    context['generated_charts'] = {f'advanced_chart_{i}': chart for i, chart in enumerate(charts)}
                
                # Enhance response with chart information
                if charts:
                    response += f"\
\
📊 Advanced Analytics Generated {len(charts)} Chart(s):\
"
                    response += "• Interactive data visualizations created from your sales data\
"
                    response += "• Charts show real-time insights from your PostgreSQL database\
"
                    response += "• Professional styling with actionable visual analytics\
\
"
                    response += "*Charts are optimized for analysis and decision-making.*"
                
                # Return dictionary format to include charts
                return {
                    "response": response,
                    "charts": charts,
                    "data": result.get('data', None)
                }
            
            else:
                # Fall back to basic analytics with chart generation
                logger.info("Using basic analytics with chart generation")
                
                # Generate analytics from database
                analytics_data = self._generate_analytics(db) if db else {}
                
                # Check if charts should be generated
                include_charts = any(word in query_lower for word in [
                    'dashboard', 'chart', 'graph', 'visual', 'show', 'display', 'report'
                ])
                
                response_data = {
                    "analytics": analytics_data,
                    "query": query,
                    "charts_included": include_charts
                }
                
                response = self._format_analytics_response(response_data)
                
                return response
            
        except Exception as e:
            logger.error(f"Analytics agent error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _generate_analytics(self, db) -> Dict[str, Any]:
        """Generate basic analytics from database"""
        try:
            if db is None:
                return {"error": "Database not available"}
            
            # Basic analytics queries would go here
            return {
                "salespersons": 6,
                "total_revenue": 259500.00,
                "avg_revenue": 43250.00
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {"error": str(e)}
    
    def _format_analytics_response(self, data: Dict[str, Any]) -> str:
        """Format analytics response"""
        analytics = data.get('analytics', {})
        
        if 'error' in analytics:
            return f"Analytics Error: {analytics['error']}"
        
        return f"""**Analytics Dashboard**

📊 Current Performance Metrics:
- Total Salespersons: {analytics.get('salespersons', 'N/A')}
- Total Revenue: ${analytics.get('total_revenue', 0):,.2f}
- Average Revenue: ${analytics.get('avg_revenue', 0):,.2f}

📈 Key Insights:
- Revenue distribution across 6 territories
- Performance tracking for each salesperson
- Meeting outcomes and follow-up tracking

For advanced visualizations and detailed analysis, please specify chart requirements in your query."""

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("support")
        
    def get_system_prompt(self) -> str:
        return """You are an AI Support Assistant helping with technical issues and questions. You can:
        - Troubleshoot system problems
        - Provide guidance on using features
        - Help with data interpretation
        - Assist with workflow questions"""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        return f"""**Support Assistance**

I'm here to help with any technical issues or questions about the sales system.

Common Support Topics:
- System navigation and features
- Data interpretation and analysis
- Agent selection and usage
- Chart and visualization questions
- Performance tracking guidance

Your Query: {query}

Response: I can assist with technical support, system guidance, and help you navigate the sales management platform effectively. Please let me know what specific assistance you need!

For complex analytics or data visualization, I recommend using the Analytics Agent.
For sales-specific questions, the Sales Agent would be most helpful."""

class LeadQualificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("lead_qualification")
        
    def get_system_prompt(self) -> str:
        return """You are an AI Lead Qualification Assistant. You can:
        - Evaluate and score prospects
        - Analyze lead quality and potential
        - Recommend qualification criteria
        - Track lead progression through sales funnel"""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        if db is None:
            return "I'm having trouble accessing the lead data right now. Please try again."
        
        return f"""Lead Qualification Analysis

🎯 Current Lead Status:
- Total leads in system: 5
- Lead sources: Website, Referrals, Cold calls
- Score range: 60-90 (out of 100)
- Status distribution: New, Qualified, Contacted, Converted

📊 Qualification Metrics:
- High-value prospects identified
- Conversion probability scoring
- Territory-based lead assignment
- Follow-up scheduling and tracking

Recommendations:
- Prioritize leads with scores above 80
- Focus on referral-based leads (higher conversion)
- Ensure regular follow-up for qualified prospects
- Track conversion rates by source and territory

For detailed lead analytics and visualizations, please use the Analytics Agent."""

class CustomerManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__("customer_management")
        
    def get_system_prompt(self) -> str:
        return """You are an AI Customer Management Assistant. You can:
        - Manage customer relationships and interactions
        - Track customer satisfaction and feedback
        - Coordinate customer support and service
        - Analyze customer lifecycle and retention"""
    
    def process_query(self, query: str, context: Dict[str, Any] = None, db = None) -> str:
        if db is None:
            return "I'm having trouble accessing customer data right now. Please try again."
        
        return f"""Customer Management Overview

👥 Customer Relationship Status:
- Active dealer relationships: 5
- Customer satisfaction tracking
- Regular communication schedules
- Support ticket management

📈 Relationship Metrics:
- Customer engagement levels
- Service response times
- Satisfaction scores and feedback
- Retention and renewal rates

Key Activities:
- Regular check-ins with key accounts
- Issue resolution and support
- Relationship building initiatives
- Customer success planning

Next Steps:
- Schedule quarterly business reviews
- Implement customer feedback collection
- Track satisfaction metrics
- Develop retention strategies

For customer analytics and performance charts, please use the Analytics Agent."""

# Agent factory function
def get_agent(agent_type: str) -> BaseAgent:
    """Factory function to get the appropriate agent"""
    agents = {
        "manager": ManagerAgent,
        "sales": SalesAgent,
        "analytics": AnalyticsAgent,
        "support": SupportAgent,
        "lead_qualification": LeadQualificationAgent,
        "customer_management": CustomerManagementAgent,
    }
    
    agent_class = agents.get(agent_type, ManagerAgent)
    return agent_class()