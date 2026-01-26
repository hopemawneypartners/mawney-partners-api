#!/usr/bin/env python3
"""
Seed the database with initial users
Run this script to create users in the database with the correct passwords
"""
from database.models import User, SessionLocal, init_db
from routes.auth import hash_password
import uuid

# User credentials from the credentials document
USERS = [
    {
        "id": "user_hope",
        "email": "hg@mawneypartners.com",
        "name": "Hope Gilbert",
        "password": "Mawney2024!HopeSecure"
    },
    {
        "id": "user_josh",
        "email": "jt@mawneypartners.com",
        "name": "Joshua Trister",
        "password": "Trister2024!JoshSecure"
    },
    {
        "id": "user_rachel",
        "email": "finance@mawneypartners.com",
        "name": "Rachel Trister",
        "password": "Finance2024!RachelSecure"
    },
    {
        "id": "user_jack",
        "email": "jd@mawneypartners.com",
        "name": "Jack Dalby",
        "password": "Dalby2024!JackSecure"
    },
    {
        "id": "user_harry",
        "email": "he@mawneypartners.com",
        "name": "Harry Edleman",
        "password": "Edleman2024!HarrySecure"
    },
    {
        "id": "user_tyler",
        "email": "tjt@mawneypartners.com",
        "name": "Tyler Johnson Thomas",
        "password": "Thomas2024!TylerSecure"
    }
]

def seed_users():
    """Create users in the database"""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        created_count = 0
        updated_count = 0
        
        for user_data in USERS:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                # Update password if user exists
                existing_user.password_hash = hash_password(user_data["password"])
                existing_user.is_active = True
                existing_user.is_deleted = False
                updated_count += 1
                print(f"✅ Updated user: {user_data['email']}")
            else:
                # Create new user
                new_user = User(
                    id=user_data["id"],
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    roles=['user'],
                    is_active=True,
                    is_deleted=False
                )
                db.add(new_user)
                created_count += 1
                print(f"✅ Created user: {user_data['email']}")
        
        db.commit()
        print(f"\n🎉 Successfully seeded users: {created_count} created, {updated_count} updated")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
