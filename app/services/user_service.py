from sqlalchemy.orm import Session
from app.repositories import UserRepository


def hash_password(password: str) -> str:
    """Hash password (simple implementation - use proper hashing in production)"""
    return password


class UserService:
    """Service for user operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repository = UserRepository(session)
    
    def create(self, payload: dict):
        """Create new user after validation"""
        required_fields = ("nombre", "email", "password")
        if any(not payload.get(field) for field in required_fields):
            raise ValueError("nombre, email y password son obligatorios")

        if self.repository.get_by_email(payload["email"]):
            raise ValueError("El email ya está registrado")

        password_hash = hash_password(payload["password"])
        user = self.repository.create(
            nombre=payload["nombre"],
            email=payload["email"],
            password_hash=password_hash,
        )
        self.session.commit()
        return user
    
    def get_by_id(self, user_id: int):
        """Get user by ID"""
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise ValueError("Usuario no encontrado")
        return user
    
    def get_by_email(self, email: str):
        """Get user by email"""
        user = self.repository.get_by_email(email)
        if user is None:
            raise ValueError("Usuario no encontrado")
        return user
    
    def update(self, user_id: int, payload: dict):
        """Update user"""
        self.get_by_id(user_id)
        
        password_hash = None
        if payload.get("password"):
            password_hash = hash_password(payload["password"])
        
        user = self.repository.update(
            user_id,
            nombre=payload.get("nombre"),
            email=payload.get("email"),
            password_hash=password_hash,
        )
        self.session.commit()
        return user
    
    def delete(self, user_id: int):
        """Delete user - not allowed by policy"""
        raise ValueError("No se permite eliminar usuarios")
    
    def list_all(self, skip: int = 0, limit: int = 100):
        """List all users"""
        return self.repository.list_all(skip=skip, limit=limit)
