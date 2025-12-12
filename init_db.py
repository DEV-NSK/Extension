# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from app import create_app
# from database.models import db

# app = create_app()

# with app.app_context():
#     print("Creating database tables...")
#     db.create_all()
#     print("Database tables created successfully!")
    
#     # Create initial admin user if needed
#     from database.models import User
#     import uuid
    
#     admin_user = User.query.filter_by(user_id='admin').first()
#     if not admin_user:
#         admin_user = User(
#             user_id='admin',
#             session_id=str(uuid.uuid4())
#         )
#         db.session.add(admin_user)
#         db.session.commit()
#         print("Admin user created!")
    
#     print("Database initialization complete!")





#!/usr/bin/env python3
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db

app = create_app()

with app.app_context():
    print("Creating database tables for PostgreSQL...")
    try:
        # Drop all tables first (for clean setup)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        print("\nTables created:")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()