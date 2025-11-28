"""
Migration Base Class
"""
from sqlalchemy import text


class Migration:
    """
    Base migration class
    
    Supports two styles:
    
    Style 1 - With self.execute():
        class CreateUsersTable(Migration):
            def up(self):
                self.execute('''
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255)
                    )
                ''')
            
            def down(self):
                self.execute('DROP TABLE users')
    
    Style 2 - With engine parameter:
        class CreateUsersTable(Migration):
            def up(self, engine):
                with engine.connect() as conn:
                    conn.execute(text('CREATE TABLE users (...)'))
                    conn.commit()
    """
    
    def __init__(self):
        self._engine = None
    
    def set_engine(self, engine):
        """Set engine for self.execute() style"""
        self._engine = engine
    
    def execute(self, query):
        """Execute raw SQL - for self.execute() style migrations"""
        if not self._engine:
            raise RuntimeError("Engine not set. Use set_engine() first.")
        
        with self._engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
    
    def up(self, engine=None):
        """Run the migration - override this in child class"""
        if engine:
            self._engine = engine
        # Child classes should override this method
        pass
    
    def down(self, engine=None):
        """Rollback the migration - override this in child class"""
        if engine:
            self._engine = engine
        # Child classes should override this method
        pass
