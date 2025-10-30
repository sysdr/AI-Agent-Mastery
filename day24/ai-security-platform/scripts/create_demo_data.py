#!/usr/bin/env python3
import sys
sys.path.append('backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, ComplianceRule
from app.auth.auth_service import auth_service
from app.compliance.compliance_service import compliance_service, ComplianceType

# Database setup
DATABASE_URL = "postgresql://postgres:password@localhost/ai_security"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_demo_data():
    db = SessionLocal()
    
    # Create admin user
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=auth_service.get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    
    # Create regular user
    regular_user = User(
        email="user@example.com", 
        username="user",
        hashed_password=auth_service.get_password_hash("user123"),
        role="user",
        is_active=True
    )
    
    db.add(admin_user)
    db.add(regular_user)
    db.commit()
    
    # Setup default compliance rules
    compliance_service.setup_default_rules(db)
    
    print("✅ Demo data created successfully!")
    print("Admin: admin@example.com / admin123")
    print("User: user@example.com / user123")
    
    db.close()

if __name__ == "__main__":
    create_demo_data()
