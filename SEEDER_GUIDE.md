# Database Seeder Guide

## Overview
Seeder system untuk populate database dengan data awal (admin account, sample data, etc).

## Structure
```
database/seeders/
├── __init__.py
├── Seeder.py           # Base seeder class
├── AdminSeeder.py      # Create admin account
└── DatabaseSeeder.py   # Run all seeders
```

## Admin Account
Created by `AdminSeeder`:
- **Email:** admin@larathon.app
- **Password:** admin123
- **Role:** admin
- **Name:** Admin

## Commands

### Run All Seeders
```bash
python artisan.py seed
# or
python artisan.py db:seed
```

### Run Specific Seeder
```bash
python artisan.py seed --class AdminSeeder
# or
python artisan.py db:seed --class AdminSeeder
```

## Usage Flow

### 1. First Time Setup
```bash
# Run migrations
python artisan.py migrate

# Run seeders
python artisan.py seed
```

### 2. Login with Admin
```
http://localhost:8000/login
Email: admin@larathon.app
Password: admin123
```

### 3. Admin Access
Admin users can:
- Access admin routes (with `admin` middleware)
- Manage all content
- Access admin dashboard (when created)

## Creating New Seeders

### Example: UserSeeder
```python
"""
User Seeder - Create sample users
"""
from database.seeders.Seeder import Seeder
from app.Models.User import User


class UserSeeder(Seeder):
    """Seed sample users"""
    
    async def run(self):
        """Run the user seeder"""
        self.info("Seeding sample users...")
        
        users = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'password': 'password',
                'role': 'user'
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'password': 'password',
                'role': 'user'
            }
        ]
        
        for user_data in users:
            try:
                existing = await User.find_by_email(user_data['email'])
                if existing:
                    self.warning(f"User already exists: {user_data['email']}")
                    continue
                
                user = await User.create_user(
                    name=user_data['name'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role']
                )
                
                self.success(f"Created user: {user.email}")
                
            except Exception as e:
                self.error(f"Failed to create {user_data['email']}: {e}")
```

### Add to DatabaseSeeder
```python
from database.seeders.UserSeeder import UserSeeder

class DatabaseSeeder(Seeder):
    async def run(self):
        print("\n🌱 Seeding database...")
        
        # Admin
        admin_seeder = AdminSeeder()
        await admin_seeder.run()
        
        # Users
        user_seeder = UserSeeder()
        await user_seeder.run()
        
        print("✅ Database seeded successfully!\n")
```

## Base Seeder Methods

### Helper Methods
```python
self.info("Info message")      # ℹ️ Info message
self.success("Success!")        # ✅ Success!
self.error("Error occurred")    # ❌ Error occurred
self.warning("Warning!")        # ⚠️ Warning!
```

### Call Other Seeders
```python
self.call(UserSeeder)
```

## Features

### Idempotent
Seeders can be run multiple times safely:
- Checks if data already exists
- Skips if found
- No duplicate data

### Error Handling
```python
try:
    # Create data
    user = await User.create_user(...)
    self.success("Created!")
except Exception as e:
    self.error(f"Failed: {e}")
    raise  # Re-raise to stop execution
```

### Async Support
All seeders are async:
```python
async def run(self):
    user = await User.create_user(...)
```

## Best Practices

1. **Check Before Create**
   ```python
   existing = await User.find_by_email(email)
   if existing:
       self.warning(f"Already exists: {email}")
       return
   ```

2. **Use Try-Catch**
   ```python
   try:
       # Create data
   except Exception as e:
       self.error(f"Failed: {e}")
   ```

3. **Clear Messages**
   ```python
   self.info("Creating admin account...")
   self.success(f"Admin created: {admin.email}")
   ```

4. **Meaningful Data**
   - Use realistic names
   - Valid emails
   - Secure passwords (even in dev)

## Common Use Cases

### 1. Admin Account
✅ Already implemented in `AdminSeeder`

### 2. Sample Users
For testing user features

### 3. Sample Posts
For testing CRUD operations

### 4. Categories/Tags
For taxonomies

### 5. Settings
Default application settings

## Testing

### After Seeding
```bash
# Check in SQLite
sqlite3 database/database.sqlite

sqlite> SELECT * FROM users;
sqlite> SELECT email, role FROM users WHERE role='admin';
```

### Verify Login
1. Start server: `python artisan.py serve`
2. Go to: `http://localhost:8000/login`
3. Login with admin credentials
4. Should access protected routes

## Troubleshooting

### Error: Seeder class not found
```bash
# Make sure __init__.py exists
touch database/seeders/__init__.py
```

### Error: User already exists
This is expected! Seeder is working correctly.
It prevents duplicate accounts.

### Error: Database not found
```bash
# Run migrations first
python artisan.py migrate
```

## Summary

✅ **AdminSeeder** creates admin account  
✅ **Idempotent** - safe to run multiple times  
✅ **Extensible** - easy to add more seeders  
✅ **Error handling** - clear messages  
✅ **Laravel-style** - familiar commands  

**Ready to seed your database!** 🌱
