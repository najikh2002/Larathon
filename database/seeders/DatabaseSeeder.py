"""
Database Seeder - Run all seeders
"""
from database.seeders.Seeder import Seeder
from database.seeders.AdminSeeder import AdminSeeder
import asyncio


class DatabaseSeeder(Seeder):
    """Main database seeder"""
    
    async def run(self):
        """Run all seeders"""
        print("\n🌱 Seeding database...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Run admin seeder
        admin_seeder = AdminSeeder()
        await admin_seeder.run()
        
        # Add more seeders here
        # user_seeder = UserSeeder()
        # await user_seeder.run()
        
        # post_seeder = PostSeeder()
        # await post_seeder.run()
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ Database seeded successfully!\n")


if __name__ == "__main__":
    """Run all seeders"""
    seeder = DatabaseSeeder()
    asyncio.run(seeder.run())
