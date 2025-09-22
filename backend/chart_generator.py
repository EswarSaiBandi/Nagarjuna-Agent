import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Salesperson, Dealer, Meeting, Lead
import structlog
import os

logger = structlog.get_logger()

class ChartGenerator:
    def __init__(self):
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create charts directory if it doesn't exist
        os.makedirs('/tmp/charts', exist_ok=True)
    
    def generate_sales_dashboard_charts(self, db: Session) -> dict:
        """Generate comprehensive dashboard charts"""
        try:
            charts = {}
            
            # Revenue by Salesperson Chart
            charts['revenue_chart'] = self.create_revenue_chart(db)
            
            # Meeting Outcomes Chart
            charts['meetings_chart'] = self.create_meetings_chart(db)
            
            # Lead Status Distribution
            charts['leads_chart'] = self.create_leads_chart(db)
            
            # Regional Performance Chart
            charts['regional_chart'] = self.create_regional_chart(db)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating dashboard charts: {e}")
            return {}
    
    def create_revenue_chart(self, db: Session) -> str:
        """Create revenue by salesperson bar chart"""
        try:
            # Mock data for demonstration
            data = {
                'names': ['Emily Davis', 'Carol Williams', 'Alice Johnson', 'Bob Smith', 'Frank Miller', 'David Brown'],
                'revenue': [61000, 52000, 45000, 38500, 33500, 29000]
            }
            
            plt.figure(figsize=(12, 8))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            bars = plt.bar(data['names'], data['revenue'], color=colors)
            
            # Add value labels on bars
            for bar, value in zip(bars, data['revenue']):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                        f'${value:,}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Revenue by Salesperson', fontsize=16, fontweight='bold')
            plt.xlabel('Salesperson', fontsize=12)
            plt.ylabel('Revenue ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            return self._plot_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating revenue chart: {e}")
            return ""
    
    def create_meetings_chart(self, db: Session) -> str:
        """Create meeting outcomes pie chart"""
        try:
            # Mock data
            outcomes = ['Successful', 'Follow-up Needed', 'No Interest', 'Rescheduled']
            counts = [3, 1, 1, 0]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            plt.figure(figsize=(10, 8))
            plt.pie(counts, labels=outcomes, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Meeting Outcomes Distribution', fontsize=16, fontweight='bold')
            
            return self._plot_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating meetings chart: {e}")
            return ""
    
    def create_leads_chart(self, db: Session) -> str:
        """Create lead status distribution chart"""
        try:
            # Mock data
            statuses = ['New', 'Qualified', 'Contacted', 'Converted']
            counts = [1, 2, 1, 1]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(statuses, counts, color=colors)
            
            # Add value labels
            for bar, count in zip(bars, counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.title('Lead Status Distribution', fontsize=16, fontweight='bold')
            plt.xlabel('Status', fontsize=12)
            plt.ylabel('Number of Leads', fontsize=12)
            plt.grid(axis='y', alpha=0.3)
            
            return self._plot_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating leads chart: {e}")
            return ""
    
    def create_regional_chart(self, db: Session) -> str:
        """Create regional performance chart"""
        try:
            # Mock data
            regions = ['North', 'South', 'East', 'West', 'Central', 'Northeast']
            revenue = [45000, 38500, 52000, 29000, 61000, 33500]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(regions, revenue, color=colors)
            
            # Add value labels
            for bar, value in zip(bars, revenue):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                        f'${value:,}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Revenue by Region', fontsize=16, fontweight='bold')
            plt.xlabel('Region', fontsize=12)
            plt.ylabel('Revenue ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            return self._plot_to_base64()
            
        except Exception as e:
            logger.error(f"Error creating regional chart: {e}")
            return ""
    
    def _plot_to_base64(self) -> str:
        """Convert current matplotlib plot to base64 string"""
        try:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            # Encode to base64
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()  # Important: close the figure to free memory
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            logger.error(f"Error converting plot to base64: {e}")
            return ""