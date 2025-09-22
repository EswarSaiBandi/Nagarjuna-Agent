from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
import uuid
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Import database models and dependencies
from database import SessionLocal, get_db, get_simple_db, create_tables, Salesperson, Dealer, Meeting, Lead, ConversationHistory, SalespersonLoginSession, SalesRecord

# Initialize FastAPI app
app = FastAPI(title="Sales Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (with error handling)
try:
    create_tables()
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("🔄 Continuing with fallback data...")

# API Router
api_router = APIRouter(prefix="/api")

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "manager"  # Default to manager agent for routing
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    session_id: str
    charts: Optional[List[str]] = []  # List of base64 chart images
    data: Optional[List[Dict]] = None  # Raw data for advanced processing

class LoginSessionCreate(BaseModel):
    salesperson_id: str
    login_time: datetime
    location: Optional[str] = None
    device_info: Optional[str] = None

class LoginSessionUpdate(BaseModel):
    logout_time: datetime

class SalesRecordCreate(BaseModel):
    salesperson_id: str
    sale_amount: float
    product_name: str
    customer_name: str
    sale_date: datetime
    commission_rate: float = 0.1

class SalespersonCreate(BaseModel):
    name: str
    region: str
    gps_location: str
    phone: str
    email: str

class SalespersonResponse(BaseModel):
    id: str
    name: str
    region: str
    gps_location: str
    phone: str
    email: str
    total_revenue: float
    monthly_target: float
    is_active: bool
    created_at: datetime

class DealerCreate(BaseModel):
    name: str
    location: str
    contact_person: str
    phone: str
    email: str
    status: str = "active"

class DealerResponse(BaseModel):
    id: str
    name: str
    location: str
    contact_person: str
    phone: str
    email: str
    status: str
    created_at: datetime

class MeetingCreate(BaseModel):
    salesperson_id: str
    dealer_id: Optional[str] = None
    notes: str
    outcome: str
    follow_up_date: Optional[datetime] = None
    location: str
    duration_minutes: int

class MeetingResponse(BaseModel):
    id: str
    salesperson_id: str
    dealer_id: Optional[str] = None
    notes: str
    outcome: str
    follow_up_date: Optional[datetime] = None
    location: str
    duration_minutes: int
    created_at: datetime

class LeadCreate(BaseModel):
    name: str
    company: str
    phone: str
    email: str
    location: str
    source: str
    status: str = "new"
    score: int = 50
    notes: str = ""
    assigned_to: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    name: str
    company: str
    phone: str
    email: str
    location: str
    source: str
    status: str
    score: int
    notes: str
    assigned_to: Optional[str] = None
    created_at: datetime

class LoginSessionResponse(BaseModel):
    id: str
    salesperson_id: str
    login_time: datetime
    logout_time: Optional[datetime] = None
    session_duration_minutes: Optional[int] = None
    location: Optional[str] = None
    device_info: Optional[str] = None

class SalesRecordResponse(BaseModel):
    id: str
    salesperson_id: str
    sale_amount: float
    product_name: str
    customer_name: str
    sale_date: datetime
    commission_rate: float
    commission_amount: float

# In-memory conversation history (in production, use a proper database)
conversation_history: Dict[str, List[Dict]] = {}

# Import agents
from agents import get_agent

# Advanced analytics endpoint
@api_router.post("/analytics/advanced")
async def advanced_analytics_query(request: ChatRequest):
    try:
        from advanced_analytics import AdvancedAnalyticsAgent
        from database import get_simple_db
        
        # Get simple database session (may be None)
        db = get_simple_db()
        
        # Get Emergent API key
        emergent_key = os.getenv("EMERGENT_LLM_KEY")
        if not emergent_key:
            raise HTTPException(status_code=500, detail="Emergent API key not configured")
        
        # Initialize advanced analytics agent
        advanced_agent = AdvancedAnalyticsAgent(emergent_key)
        
        # Process the query with database session
        result = advanced_agent.process_query(request.message, db=db)
        
        # Close database connection if it exists
        if db is not None:
            try:
                db.close()
            except:
                pass
        
        return result
        
    except Exception as e:
        logging.error(f"Advanced analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing advanced analytics: {str(e)}")

# Chat endpoint - Main AI interaction
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize conversation history for session
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Get simple database session (may be None)
        from database import get_simple_db
        db = get_simple_db()
        
        # Get the appropriate agent
        agent = get_agent(request.agent_type)
        
        # Process the query
        result = agent.process_query(request.message, db=db)
        
        # Handle different response types
        if isinstance(result, dict) and "response" in result:
            # Advanced analytics response with charts
            response_text = result["response"]
            charts = result.get("charts", [])
            raw_data = result.get("data", None)
            
            # Convert tuple data to dict format for Pydantic validation
            if raw_data and isinstance(raw_data, list) and raw_data:
                if isinstance(raw_data[0], tuple) and len(raw_data[0]) >= 2:
                    data = [{"name": str(row[0]), "value": float(row[1])} for row in raw_data]
                else:
                    data = raw_data
            else:
                data = None
        else:
            # Simple string response
            response_text = str(result)
            charts = []
            data = None
        
        # Save conversation to database (save text response only)
        if db is not None:
            try:
                conversation = ConversationHistory(
                    session_id=session_id,
                    user_message=request.message,
                    agent_response=response_text,
                    agent_type=agent.agent_type
                )
                db.add(conversation)
                db.commit()
            except Exception as e:
                logging.warning(f"Could not save conversation to database: {e}")
        
        # Close database connection if it exists
        if db is not None:
            try:
                db.close()
            except:
                pass
        
        # Update in-memory conversation history
        conversation_history[session_id].append({
            "role": "user",
            "content": request.message
        })
        conversation_history[session_id].append({
            "role": "assistant",
            "content": response_text,
            "agent_type": agent.agent_type
        })
        
        return ChatResponse(
            response=response_text,
            agent_type=agent.agent_type,
            session_id=session_id,
            charts=charts,
            data=data
        )
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")

# Salespersons endpoints
@api_router.get("/salespersons", response_model=List[SalespersonResponse])
async def get_salespersons(db: SessionLocal = Depends(get_db)):
    # Define mock data for fallback use
    from datetime import datetime
    mock_salespersons = [
        SalespersonResponse(
            id="1",
            name="Alice Johnson",
            region="North", 
            gps_location="12.9716,77.5946",
            phone="+1-555-0101",
            email="alice@company.com",
            total_revenue=45000.00,
            monthly_target=15000.00,
            is_active=True,
            created_at=datetime.now()
        ),
        SalespersonResponse(
            id="2",
            name="Bob Smith",
            region="South",
            gps_location="13.0827,80.2707", 
            phone="+1-555-0102",
            email="bob@company.com",
            total_revenue=38500.00,
            monthly_target=12000.00,
            is_active=True,
            created_at=datetime.now()
        ),
        SalespersonResponse(
            id="3",
            name="Carol Williams",
            region="East",
            gps_location="22.5726,88.3639",
            phone="+1-555-0103",
            email="carol@company.com", 
            total_revenue=52000.00,
            monthly_target=18000.00,
            is_active=True,
            created_at=datetime.now()
        ),
        SalespersonResponse(
            id="4", 
            name="David Brown",
            region="West",
            gps_location="19.0760,72.8777",
            phone="+1-555-0104", 
            email="david@company.com",
            total_revenue=29000.00,
            monthly_target=10000.00,
            is_active=False,
            created_at=datetime.now()
        ),
        SalespersonResponse(
            id="5",
            name="Emily Davis", 
            region="Central",
            gps_location="23.2599,77.4126",
            phone="+1-555-0105",
            email="emily@company.com",
            total_revenue=61000.00,
            monthly_target=20000.00,
            is_active=True,
            created_at=datetime.now()
        ),
        SalespersonResponse(
            id="6",
            name="Frank Miller",
            region="Northeast", 
            gps_location="26.1445,91.7362",
            phone="+1-555-0106",
            email="frank@company.com",
            total_revenue=33500.00,
            monthly_target=14000.00,
            is_active=True,
            created_at=datetime.now()
        )
    ]
    
    # Check if database is available
    if db is None:
        return mock_salespersons
    
    try:
        salespersons = db.query(Salesperson).all()
        return [
            SalespersonResponse(
                id=str(sp.id),
                name=sp.name,
                region=sp.region,
                gps_location=sp.gps_location,
                phone=sp.phone,
                email=sp.email,
                total_revenue=float(sp.total_revenue or 0),
                monthly_target=float(sp.monthly_target or 0),
                is_active=sp.is_active,
                created_at=sp.created_at
            ) for sp in salespersons
        ]
    except Exception as e:
        return mock_salespersons

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)