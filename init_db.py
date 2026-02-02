#!/usr/bin/env python
"""
Initialize database schema
Run from project root: python init_db.py
"""
import sys
from pathlib import Path
from sqlalchemy import text

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.database import engine, Base
from backend.models import db_models

print("🔧 Initializing database schema...")
print(f"📁 Database: {engine.url}")

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema created successfully!")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection verified!")
        
    print("\n📋 Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  • {table.name}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
