"""
Migration: create_posts_table
"""
from vendor.Illuminate.Database.Migration import Migration


class CreatePostsTable(Migration):
    """Create posts table for content management"""
    
    def up(self):
        """Run the migrations"""
        query = """
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            slug VARCHAR(500) UNIQUE NOT NULL,
            content TEXT,
            excerpt TEXT,
            featured_image VARCHAR(500),
            status VARCHAR(50) DEFAULT 'draft',
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute(query)
        
        # Create indexes
        self.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_posts_published_at ON posts(published_at)")
    
    def down(self):
        """Reverse the migrations"""
        self.execute("DROP TABLE IF EXISTS posts CASCADE")
