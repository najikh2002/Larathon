"""
Base Model Class for Database Operations
Simple ORM-like functionality for database models
"""
from typing import Optional, List, Dict, Any
from config.database import get_database_url
import psycopg2
import psycopg2.extras
from datetime import datetime


class Model:
    """
    Base Model class for database operations
    
    Attributes:
        table: Table name (must be set in child class)
        fillable: List of fillable fields
        hidden: List of fields to hide in output
    """
    
    table = None  # Must be overridden in child class
    fillable = []
    hidden = []
    
    def __init__(self, **kwargs):
        """Initialize model with data"""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def get_connection(cls):
        """Get database connection"""
        db_url = get_database_url()
        
        # psycopg2 doesn't accept SQLAlchemy-style URLs
        # Remove +psycopg2 from the URL
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql://')
        db_url = db_url.replace('mysql+pymysql://', 'mysql://')
        
        conn = psycopg2.connect(db_url)
        return conn
    
    @classmethod
    async def all(cls) -> List['Model']:
        """Get all records"""
        conn = cls.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute(f"SELECT * FROM {cls.table}")
            rows = cursor.fetchall()
            return [cls(**dict(row)) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    async def find(cls, id: int) -> Optional['Model']:
        """Find record by ID"""
        conn = cls.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute(f"SELECT * FROM {cls.table} WHERE id = %s", (id,))
            row = cursor.fetchone()
            return cls(**dict(row)) if row else None
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def where(cls, column: str, value: Any):
        """Start a query builder (returns QueryBuilder)"""
        return QueryBuilder(cls, column, value)
    
    @classmethod
    async def create(cls, data: Dict[str, Any]) -> 'Model':
        """Create new record"""
        # Filter only fillable fields
        filtered_data = {k: v for k, v in data.items() if k in cls.fillable}
        
        conn = cls.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            columns = ', '.join(filtered_data.keys())
            placeholders = ', '.join(['%s'] * len(filtered_data))
            values = tuple(filtered_data.values())
            
            query = f"""
                INSERT INTO {cls.table} ({columns})
                VALUES ({placeholders})
                RETURNING *
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            row = cursor.fetchone()
            return cls(**dict(row))
        finally:
            cursor.close()
            conn.close()
    
    async def save(self) -> bool:
        """Save (update) existing record"""
        if not hasattr(self, 'id'):
            raise ValueError("Cannot save model without ID")
        
        # Get fillable data
        data = {k: getattr(self, k) for k in self.fillable if hasattr(self, k)}
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            values = tuple(data.values()) + (self.id,)
            
            query = f"""
                UPDATE {self.table}
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, values)
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()
    
    async def delete(self) -> bool:
        """Delete this record"""
        if not hasattr(self, 'id'):
            raise ValueError("Cannot delete model without ID")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"DELETE FROM {self.table} WHERE id = %s", (self.id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {}
        for key, value in self.__dict__.items():
            if key not in self.hidden and not key.startswith('_'):
                # Convert datetime to string
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    data[key] = value
        return data
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_dict()}>"


class QueryBuilder:
    """
    Simple query builder for Model
    Supports basic where and order_by operations
    """
    
    def __init__(self, model_class, column: str = None, value: Any = None):
        self.model_class = model_class
        self.wheres = []
        self.order_bys = []
        self.limit_value = None
        
        if column and value is not None:
            self.wheres.append((column, '=', value))
    
    def where(self, column: str, operator_or_value: Any, value: Any = None):
        """Add WHERE clause"""
        if value is None:
            # where('column', 'value') -> where('column', '=', 'value')
            operator = '='
            value = operator_or_value
        else:
            operator = operator_or_value
        
        self.wheres.append((column, operator, value))
        return self
    
    def order_by(self, column: str, direction: str = 'asc'):
        """Add ORDER BY clause"""
        self.order_bys.append((column, direction.upper()))
        return self
    
    def limit(self, limit: int):
        """Add LIMIT clause"""
        self.limit_value = limit
        return self
    
    async def get(self) -> List[Model]:
        """Execute query and get results"""
        conn = self.model_class.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            query = f"SELECT * FROM {self.model_class.table}"
            params = []
            
            # Add WHERE clauses
            if self.wheres:
                where_parts = []
                for column, operator, value in self.wheres:
                    where_parts.append(f"{column} {operator} %s")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_parts)
            
            # Add ORDER BY
            if self.order_bys:
                order_parts = [f"{col} {direction}" for col, direction in self.order_bys]
                query += " ORDER BY " + ", ".join(order_parts)
            
            # Add LIMIT
            if self.limit_value:
                query += f" LIMIT {self.limit_value}"
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self.model_class(**dict(row)) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    async def first(self) -> Optional[Model]:
        """Get first result"""
        self.limit_value = 1
        results = await self.get()
        return results[0] if results else None
    
    async def count(self) -> int:
        """Count matching records"""
        conn = self.model_class.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT COUNT(*) FROM {self.model_class.table}"
            params = []
            
            if self.wheres:
                where_parts = []
                for column, operator, value in self.wheres:
                    where_parts.append(f"{column} {operator} %s")
                    params.append(value)
                query += " WHERE " + " AND ".join(where_parts)
            
            cursor.execute(query, tuple(params))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()
