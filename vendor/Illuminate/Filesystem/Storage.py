"""
Storage Facade
Laravel-style storage facade for file operations
"""
from typing import Optional, BinaryIO
import os


class StorageManager:
    """Storage Manager - manages multiple storage disks"""
    
    def __init__(self):
        self.disks = {}
        self.default_disk = None
        self._drivers = {}
        
    def configure(self, config: dict):
        """Configure storage from config dict"""
        from config import filesystems
        
        self.default_disk = filesystems.default
        self.disk_configs = filesystems.disks
        
    def disk(self, name: Optional[str] = None):
        """Get a disk instance"""
        disk_name = name or self.default_disk
        
        if disk_name not in self.disks:
            self.disks[disk_name] = self._create_driver(disk_name)
            
        return self.disks[disk_name]
    
    def _create_driver(self, disk_name: str):
        """Create driver instance for disk"""
        from config import filesystems
        
        if disk_name not in filesystems.disks:
            raise ValueError(f"Disk '{disk_name}' is not configured")
        
        config = filesystems.disks[disk_name]
        driver_type = config.get("driver")
        
        if driver_type == "local":
            from vendor.Illuminate.Filesystem.Drivers.LocalDriver import LocalDriver
            return LocalDriver(config)
        elif driver_type == "supabase":
            from vendor.Illuminate.Filesystem.Drivers.SupabaseDriver import SupabaseDriver
            return SupabaseDriver(config)
        elif driver_type == "s3":
            from vendor.Illuminate.Filesystem.Drivers.S3Driver import S3Driver
            return S3Driver(config)
        else:
            raise ValueError(f"Unknown driver type: {driver_type}")


class StorageFacade:
    """Storage Facade - provides static-like interface"""
    
    _manager = None
    
    @classmethod
    def _get_manager(cls):
        if cls._manager is None:
            cls._manager = StorageManager()
            cls._manager.configure({})
        return cls._manager
    
    @classmethod
    def disk(cls, name: Optional[str] = None):
        """Get a disk instance"""
        return cls._get_manager().disk(name)
    
    @classmethod
    def put(cls, path: str, contents, disk: Optional[str] = None) -> bool:
        """Store a file"""
        return cls.disk(disk).put(path, contents)
    
    @classmethod
    def get(cls, path: str, disk: Optional[str] = None):
        """Get file contents"""
        return cls.disk(disk).get(path)
    
    @classmethod
    def exists(cls, path: str, disk: Optional[str] = None) -> bool:
        """Check if file exists"""
        return cls.disk(disk).exists(path)
    
    @classmethod
    def delete(cls, path: str, disk: Optional[str] = None) -> bool:
        """Delete a file"""
        return cls.disk(disk).delete(path)
    
    @classmethod
    def url(cls, path: str, disk: Optional[str] = None) -> str:
        """Get public URL for a file"""
        return cls.disk(disk).url(path)
    
    @classmethod
    def path(cls, path: str, disk: Optional[str] = None) -> str:
        """Get full path for a file"""
        return cls.disk(disk).path(path)
    
    @classmethod
    def files(cls, directory: str = "", disk: Optional[str] = None) -> list:
        """List files in directory"""
        return cls.disk(disk).files(directory)
    
    @classmethod
    def directories(cls, directory: str = "", disk: Optional[str] = None) -> list:
        """List directories"""
        return cls.disk(disk).directories(directory)


# Singleton instance
Storage = StorageFacade
