#!/usr/bin/env python3
"""
Enhanced seed data script for the Sales Agent database
Creates comprehensive test data including salespersons, dealers, meetings, leads,
login sessions, and sales records.
"""

import os
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Salesperson, Dealer, Meeting, Lead, SalespersonLoginSession, SalesRecord
import random

load_dotenv()

def seed_enhanced_database():
    """Seed the database with enhanced comprehensive data"""
    
    try:
        # Database connection
        # DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/sales_agent_db")
        DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://hosteladmin:hostel123@localhost:5432/sales_agent_db")

        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        
        # Recreate all tables
        print("Dropping and recreating database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        print("Creating enhanced salespersons with revenue tracking...")
        salespersons = [
            Salesperson(
                name="Alice Johnson",
                region="North",
                gps_location="12.9716,77.5946",
                phone="+1-555-0101",
                email="alice@company.com",
                total_revenue=Decimal("45000.00"),
                monthly_target=Decimal("15000.00"),
                is_active=True
            ),
            Salesperson(
                name="Bob Smith",
                region="South",
                gps_location="13.0827,80.2707",
                phone="+1-555-0102",
                email="bob@company.com",
                total_revenue=Decimal("38500.00"),
                monthly_target=Decimal("12000.00"),
                is_active=True
            ),
            Salesperson(
                name="Carol Williams",
                region="East",
                gps_location="22.5726,88.3639",
                phone="+1-555-0103",
                email="carol@company.com",
                total_revenue=Decimal("52000.00"),
                monthly_target=Decimal("18000.00"),
                is_active=True
            ),
            Salesperson(
                name="David Brown",
                region="West",
                gps_location="19.0760,72.8777",
                phone="+1-555-0104",
                email="david@company.com",
                total_revenue=Decimal("29000.00"),
                monthly_target=Decimal("10000.00"),
                is_active=False
            ),
            Salesperson(
                name="Emily Davis",
                region="Central",
                gps_location="23.2599,77.4126",
                phone="+1-555-0105",
                email="emily@company.com",
                total_revenue=Decimal("61000.00"),
                monthly_target=Decimal("20000.00"),
                is_active=True
            ),
            Salesperson(
                name="Frank Miller",
                region="Northeast",
                gps_location="26.1445,91.7362",
                phone="+1-555-0106",
                email="frank@company.com",
                total_revenue=Decimal("33500.00"),
                monthly_target=Decimal("14000.00"),
                is_active=True
            )
        ]
        
        for sp in salespersons:
            db.add(sp)
        db.commit()
        db.refresh(salespersons[0])
        db.refresh(salespersons[1])
        db.refresh(salespersons[2])
        db.refresh(salespersons[3])
        db.refresh(salespersons[4])
        db.refresh(salespersons[5])
        
        print("Creating dealers with purchase history...")
        dealers = [
            Dealer(
                name="Tech Solutions Inc",
                location="Bangalore",
                contact_person="John Doe",
                phone="+91-80-12345678",
                email="john@techsolutions.com",
                status="active"
            ),
            Dealer(
                name="Global Electronics",
                location="Chennai",
                contact_person="Jane Smith",
                phone="+91-44-87654321",
                email="jane@globalelectronics.com",
                status="active"
            ),
            Dealer(
                name="Future Systems",
                location="Mumbai",
                contact_person="Mike Wilson",
                phone="+91-22-11223344",
                email="mike@futuresystems.com",
                status="prospect"
            ),
            Dealer(
                name="Smart Retail",
                location="Delhi",
                contact_person="Sarah Johnson",
                phone="+91-11-55667788",
                email="sarah@smartretail.com",
                status="active"
            ),
            Dealer(
                name="Digital Hub",
                location="Kolkata",
                contact_person="Alex Brown",
                phone="+91-33-99887766",
                email="alex@digitalhub.com",
                status="inactive"
            )
        ]
        
        for dealer in dealers:
            db.add(dealer)
        db.commit()
        for dealer in dealers:
            db.refresh(dealer)
            
        print("Creating meetings with detailed outcomes...")
        meetings = [
            Meeting(
                salesperson_id=salespersons[0].id,
                dealer_id=dealers[0].id,
                notes="Successful product demo. Customer interested in bulk purchase.",
                outcome="successful",
                follow_up_date=None,
                location="Bangalore",
                duration_minutes=90
            ),
            Meeting(
                salesperson_id=salespersons[1].id,
                dealer_id=dealers[1].id,
                notes="Need follow-up on pricing discussion. Customer requested proposal.",
                outcome="follow_up_needed",
                follow_up_date=datetime.now() + timedelta(days=7),
                location="Chennai",
                duration_minutes=60
            ),
            Meeting(
                salesperson_id=salespersons[2].id,
                dealer_id=dealers[2].id,
                notes="Initial meeting with prospect. Need to understand requirements better.",
                outcome="follow_up_needed",
                follow_up_date=datetime.now() + timedelta(days=3),
                location="Mumbai",
                duration_minutes=45
            ),
            Meeting(
                salesperson_id=salespersons[3].id,
                dealer_id=dealers[3].id,
                notes="Contract signed! Major deal closed successfully.",
                outcome="successful",
                follow_up_date=None,
                location="Delhi",
                duration_minutes=120
            ),
            Meeting(
                salesperson_id=salespersons[4].id,
                dealer_id=dealers[4].id,
                notes="Customer not interested in current offerings. Market timing issue.",
                outcome="no_interest",
                follow_up_date=None,
                location="Kolkata",
                duration_minutes=30
            )
        ]
        
        for meeting in meetings:
            db.add(meeting)
        db.commit()
        
        print("Creating leads with estimated values...")
        leads = [
            Lead(
                name="Manufacturing Corp",
                company="ManufaCorp Ltd",
                phone="+91-80-98765432",
                email="contact@manufacorp.com",
                location="Bangalore",
                source="website",
                status="new",
                score=85,
                notes="Large manufacturing company interested in ERP solution",
                assigned_to=salespersons[0].id
            ),
            Lead(
                name="Startup Hub",
                company="TechStart Inc",
                phone="+91-44-12345678",
                email="info@techstart.com",
                location="Chennai",
                source="referral",
                status="qualified",
                score=75,
                notes="Growing startup needs CRM integration",
                assigned_to=salespersons[1].id
            ),
            Lead(
                name="Retail Chain",
                company="SuperMart",
                phone="+91-22-87654321",
                email="procurement@supermart.com",
                location="Mumbai",
                source="cold_call",
                status="contacted",
                score=60,
                notes="Retail chain exploring POS solutions",
                assigned_to=salespersons[2].id
            ),
            Lead(
                name="Education Institute",
                company="Learning Academy",
                phone="+91-11-11223344",
                email="admin@learningacademy.edu",
                location="Delhi",
                source="website",
                status="qualified",
                score=70,
                notes="Educational institution seeking learning management system",
                assigned_to=salespersons[3].id
            ),
            Lead(
                name="Healthcare Solutions",
                company="Health Plus",
                phone="+91-20-99887766",
                email="contact@healthplus.com",
                location="Pune",
                source="referral",
                status="converted",
                score=90,
                notes="Healthcare provider - high priority lead converted to customer",
                assigned_to=salespersons[0].id
            )
        ]
        
        for lead in leads:
            db.add(lead)
        db.commit()
        
        # Create login sessions and sales records
        print("Creating login sessions and sales records...")
        
        # Generate login sessions for the last 30 days
        login_sessions = []
        sales_records = []
        
        for i in range(90):  # 90 login sessions over 30 days
            salesperson = random.choice(salespersons)
            login_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Create login session
            duration_minutes = random.randint(120, 480)  # 2-8 hours
            logout_time = login_date + timedelta(minutes=duration_minutes)
            
            login_session = SalespersonLoginSession(
                salesperson_id=salesperson.id,
                login_time=login_date,
                logout_time=logout_time,
                session_duration_minutes=duration_minutes,
                location=salesperson.region,
                device_info=f"{random.choice(['Desktop', 'Mobile', 'Tablet'])} - {random.choice(['Chrome', 'Firefox', 'Safari'])}"
            )
            login_sessions.append(login_session)
        
        for session in login_sessions:
            db.add(session)
        
        # Generate sales records
        products = [
            ("CRM Software", 5000, 15000),
            ("ERP System", 10000, 30000),
            ("Mobile App Development", 3000, 12000),
            ("Web Development", 2000, 8000),
            ("Database Solutions", 4000, 10000),
            ("Cloud Migration", 6000, 20000),
            ("AI Integration", 8000, 25000),
            ("Security Audit", 1500, 5000)
        ]
        
        customers = [
            "Tech Solutions Inc", "Global Electronics", "Future Systems",
            "Smart Retail", "Digital Hub", "ManufaCorp Ltd", "TechStart Inc",
            "SuperMart", "Learning Academy", "Health Plus"
        ]
        
        for i in range(25):  # 25 sales records
            salesperson = random.choice(salespersons)
            product_name, min_price, max_price = random.choice(products)
            sale_amount = Decimal(str(random.randint(min_price, max_price)))
            commission_rate = Decimal("0.10")  # 10% commission
            commission_amount = sale_amount * commission_rate
            
            sale_record = SalesRecord(
                salesperson_id=salesperson.id,
                sale_amount=sale_amount,
                product_name=product_name,
                customer_name=random.choice(customers),
                sale_date=datetime.now() - timedelta(days=random.randint(0, 90)),
                commission_rate=commission_rate,
                commission_amount=commission_amount
            )
            sales_records.append(sale_record)
        
        for record in sales_records:
            db.add(record)
        
        db.commit()
        db.close()
        
        print(f"✅ Enhanced database seeding completed successfully!")
        print(f"Created {len(salespersons)} salespersons")
        print(f"Created {len(dealers)} dealers")
        print(f"Created {len(meetings)} meetings")
        print(f"Created {len(leads)} leads with estimated values")
        print(f"Created {len(login_sessions)} login sessions")
        print(f"Created {len(sales_records)} sales records")
        
    except Exception as e:
        print(f"❌ Error seeding enhanced database: {e}")

if __name__ == "__main__":
    seed_enhanced_database()