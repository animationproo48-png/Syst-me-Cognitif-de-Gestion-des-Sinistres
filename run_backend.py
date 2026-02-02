#!/usr/bin/env python
"""
Backend startup script - Run from project root
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add backend and project root to path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

# Change to backend directory for relative imports
os.chdir(backend_dir)

# Load environment
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    print("🚀 Démarrage du serveur Insurance CRM...")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🌍 Host: {os.getenv('SERVER_HOST', '0.0.0.0')}")
    print(f"🔌 Port: {os.getenv('SERVER_PORT', '8000')}")
    print(f"📊 Database: {os.getenv('DATABASE_URL', 'sqlite:///./insurance.db')}")
    
    uvicorn.run(
        "main:app",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
