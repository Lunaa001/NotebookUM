from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UserRepository:
    """Repository for Usuario model operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def exists(self, user_id: int) -> bool:
        """Check if user exists by ID"""
        user = self.session.query(Usuario).filter(Usuario.id == user_id).first()
        return user is not None
    
    def get_by_id(self, user_id: int) -> Usuario | None:
        """Get user by ID"""
        return self.session.query(Usuario).filter(Usuario.id == user_id).first()
    
    def get_by_email(self, email: str) -> Usuario | None:
        """Get user by email"""
        return self.session.query(Usuario).filter(Usuario.email == email).first()
    
    def create(self, *, nombre: str, email: str, password_hash: str | None = None) -> Usuario:
        """Create new user"""
        user = Usuario(nombre=nombre, email=email)
        self.session.add(user)
        self.session.flush()
        return user
    
    def update(self, user_id: int, *, nombre: str | None = None, email: str | None = None, password_hash: str | None = None) -> Usuario | None:
        """Update user"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if nombre is not None:
            user.nombre = nombre
        if email is not None:
            user.email = email
        # password_hash can be added to Usuario model if needed
        
        self.session.flush()
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user by ID"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.session.delete(user)
        self.session.flush()
        return True
    
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Usuario]:
        """List all users with pagination"""
        return self.session.query(Usuario).offset(skip).limit(limit).all()
