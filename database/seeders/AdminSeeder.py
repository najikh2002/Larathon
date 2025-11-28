"""
Admin Seeder - Create default admin account
"""
from database.seeders.Seeder import Seeder
from app.Models.User import User
import asyncio


class AdminSeeder(Seeder):
    """Seed admin account"""
    
    async def run(self):
        """Run the admin seeder"""
        self.info("Seeding admin account...")
        
        try:
            # Admin credentials
            admin_email = "admin@larathon.app"
            admin_name = "Admin"
            admin_password = "admin123"
            admin_role = "admin"
            
            # Check if admin already exists
            existing_admin = await User.find_by_email(admin_email)
            
            if existing_admin:
                self.warning(f"Admin account already exists: {admin_email}")
                self.info(f"Admin ID: {existing_admin.id}")
                return
            
            # Create admin user
            admin = await User.create_user(
                name=admin_name,
                email=admin_email,
                password=admin_password,
                role=admin_role
            )
            
            self.success(f"Admin account created successfully!")
            self.info(f"Email: {admin_email}")
            self.info(f"Password: {admin_password}")
            self.info(f"Role: {admin_role}")
            self.info(f"User ID: {admin.id}")
            
        except Exception as e:
            self.error(f"Failed to create admin account: {str(e)}")
            raise


if __name__ == "__main__":
    """Run seeder directly"""
    seeder = AdminSeeder()
    asyncio.run(seeder.run())
