"""
Migration: create_users_table
"""
from vendor.Illuminate.Database.Migration import Migration


class CreateUsersTable(Migration):
    """Create users table for authentication"""
    
    def up(self):
        """Run the migrations"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            avatar VARCHAR(500),
            role VARCHAR(50) DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute(query)
        
        # Create index on email for faster lookups
        self.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    
    def down(self):
        """Reverse the migrations"""
        self.execute("DROP TABLE IF EXISTS users CASCADE")
