"""
Base Seeder Class
"""
import asyncio


class Seeder:
    """Base seeder class"""
    
    async def run(self):
        """Run the seeder - override this method"""
        raise NotImplementedError("Seeder must implement run() method")
    
    def call(self, seeder_class):
        """Call another seeder"""
        seeder = seeder_class()
        asyncio.run(seeder.run())
        
    def info(self, message):
        """Print info message"""
        print(f"   ℹ️  {message}")
    
    def success(self, message):
        """Print success message"""
        print(f"   ✅ {message}")
    
    def error(self, message):
        """Print error message"""
        print(f"   ❌ {message}")
    
    def warning(self, message):
        """Print warning message"""
        print(f"   ⚠️  {message}")
