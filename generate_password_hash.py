#!/usr/bin/env python3
"""
Utility script to generate bcrypt password hashes
Use this to create password hashes for inserting users into BigQuery
"""

import bcrypt
import sys

def generate_hash(password):
    """Generate bcrypt hash for a password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode('utf-8')

def verify_hash(password, password_hash):
    """Verify a password against its hash"""
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_password_hash.py <password>")
        print("Example: python generate_password_hash.py mypassword123")
        sys.exit(1)
    
    password = sys.argv[1]
    password_hash = generate_hash(password)
    
    print("="*50)
    print("🔐 PASSWORD HASH GENERATOR")
    print("="*50)
    print(f"Password: {password}")
    print(f"Bcrypt Hash: {password_hash}")
    print()
    
    # Verify the hash works
    if verify_hash(password, password_hash):
        print("✅ Hash verification successful")
    else:
        print("❌ Hash verification failed")
    
    print()
    print("📋 BigQuery INSERT statement:")
    print(f"""
INSERT INTO `practise-bi.user.users` (
  user_id, username, email, password_hash, role, is_active, created_at
) VALUES (
  'user_001',
  'your_username',
  'your_email@example.com',
  '{password_hash}',
  'user',
  true,
  CURRENT_TIMESTAMP(),
  NULL
);
    """)

if __name__ == "__main__":
    main() 