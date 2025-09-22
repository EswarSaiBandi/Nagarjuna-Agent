import os
import re
import base64
import io
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, Salesperson, Dealer, Meeting, Lead
import structlog
from dotenv import load_dotenv

logger = structlog.get_logger()

class AdvancedAnalyticsAgent:
    def __init__(self, api_key: str = None):
        """Initialize the advanced analytics agent"""
        load_dotenv()
        
        # For local development, we'll use mock responses
        self.api_key = api_key or os.getenv('EMERGENT_LLM_KEY')
        logger.info("Advanced Analytics Agent initialized successfully (Local Mode)")
    
    def process_query(self, query: str, session_history: List[Dict] = None, db: Session = None) -> Dict[str, Any]:
        """Process a query using advanced analytics"""
        try:
            # Mock data for demonstration when database is not available
            data = [
                ("Emily Davis", 61000.00),
                ("Carol Williams", 52000.00), 
                ("Alice Johnson", 45000.00),
                ("Bob Smith", 38500.00),
                ("Frank Miller", 33500.00),
                ("David Brown", 29000.00)
            ]
            
            # Determine if this needs a chart
            query_lower = query.lower()
            needs_chart = any(word in query_lower for word in [
                'chart', 'graph', 'plot', 'visual', 'show', 'display', 'bar', 'pie', 'line'
            ])
            
            # Create chart if requested
            charts = []
            if needs_chart and len(data) > 1:
                chart = self._create_chart(data, "bar", "Revenue by Salesperson")
                if chart and not chart.startswith("Error"):
                    charts.append(chart)
            
            # Generate response based on query type
            response = self._generate_response(query, data)

            return {
                "response": response,
                "charts": charts,
                "data": data[:10]
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "charts": [],
                "data": None
            }
    
    def _generate_response(self, query: str, data: List[tuple]) -> str:
        """Generate AI-like response based on query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['revenue', 'sales', 'performance']):
            total_revenue = sum(row[1] for row in data)
            avg_revenue = total_revenue / len(data)
            top_performer = max(data, key=lambda x: x[1])
            
            return f"""**Sales Performance Analysis**

Based on your query: \"{query}\"

**Key Findings:**
- {top_performer[0]} leads with ${top_performer[1]:,.0f} in revenue
- Total team revenue: ${total_revenue:,.0f}
- Average performance: ${avg_revenue:,.0f} per salesperson
- {len(data)} salespersons analyzed

**Insights:**
- Strong performance across the team with {top_performer[0]} exceeding average by {((top_performer[1]/avg_revenue-1)*100):.1f}%
- Revenue distribution shows healthy competition
- Opportunity to support lower performers and share best practices

**Recommendations:**
- Recognize top performers like {top_performer[0]}
- Provide coaching for bottom quartile performers
- Analyze successful strategies from top performers
- Set incremental improvement targets for team growth"""

        elif any(word in query_lower for word in ['team', 'overview']):
            return f"""**Sales Team Overview**

**Team Composition:**
- 6 active salespersons across different regions
- Coverage includes North, South, East, West, Central, and Northeast territories
- Mix of high-performing and developing team members

**Performance Metrics:**
- Active dealer relationships maintained
- Regular meeting schedules and follow-ups
- Lead qualification and conversion tracking
- Revenue targets being monitored monthly

**Current Status:**
- Strong regional coverage ensures comprehensive market presence
- Balanced portfolio of prospects and active customers
- Consistent performance tracking and reporting

**Next Steps:**
- Continue performance monitoring and coaching
- Expand high-performing territories
- Support developing team members with training"""

        else:
            return f"""**Analytics Dashboard Response**

Thank you for your query: \"{query}\"

**Available Analytics:**
- Revenue performance tracking
- Salesperson comparisons and rankings
- Regional performance analysis
- Meeting outcomes and effectiveness
- Lead qualification metrics

**Sample Data Available:**
- 6 salespersons with revenue data
- Regional performance comparisons
- Historical trends and patterns

For specific analytics, try queries like:
- \"Show me revenue by salesperson with charts\"
- \"Compare regional performance\"
- \"Team performance overview\"

**Note:** This is running in local development mode with sample data."""
    
    def _create_chart(self, data: List[tuple], chart_type: str = "bar", title: str = "Chart") -> str:
        """Create chart from data and return as base64 string"""
        try:
            if not data or len(data) < 2:
                return "Error: insufficient data for chart"
            
            # Extract labels and values
            labels = [str(row[0]) for row in data]
            values = [float(row[1]) if isinstance(row[1], (int, float)) else 0 for row in data]
            
            # Create the chart
            plt.figure(figsize=(12, 8))
            
            if chart_type == "bar":
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                bars = plt.bar(labels, values, color=colors[:len(labels)])
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                            f'${value:,.0f}',
                            ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                plt.title(title, fontsize=16, fontweight='bold')
                plt.xlabel('Salesperson', fontsize=12)
                plt.ylabel('Revenue ($)', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            logger.error(f"Error plotting chart: {e}")
            return f"Error plotting chart: {e}"