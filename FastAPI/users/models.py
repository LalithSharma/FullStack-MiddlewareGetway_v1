import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    api_details = relationship("UserAPI", back_populates="user", uselist=True)
    user_channels = relationship("UserChannel", back_populates="user", uselist=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status.value})>"

class UserAPI(Base):
    __tablename__ = 'user_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token_type = Column(String, nullable=True)
    unique_token = Column(String, unique=True, nullable=True)
    token_expiration = Column(DateTime, nullable=True)
    login_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="api_details")

    def __repr__(self):
        return f"<UserAPI(id={self.id}, user_id={self.user_id}, token_expiration={self.token_expiration})>"

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    base_url = Column(String, nullable=True)  # Add base_url column
    auth_url = Column(String, nullable=True)  # Add auth_url column
    api_key = Column(String, unique=True, nullable=True)   # Add api_key column
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    user_channels = relationship("UserChannel", back_populates="channel", uselist=True)

    def __repr__(self):
        return f"<Channel(id={self.id}, name={self.name}, status={self.status.value})>"

class UserChannel(Base):
    __tablename__ = 'user_channels'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="user_channels")
    channel = relationship("Channel", back_populates="user_channels")

    def __repr__(self):
        return f"<UserChannel(id={self.id}, user_id={self.user_id}, channel_id={self.channel_id})>"

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationship to UserRole
    user_roles = relationship("UserRole", back_populates="role")

# UserRole table
class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationship to Role
    role = relationship("Role", back_populates="user_roles")
    
class APIRoute(Base):
    __tablename__ = "api_route_path"

    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    path = Column(String(255), nullable=False)  # e.g., /clients/{client_id}/products
    cache_key_prefix = Column(String(50), nullable=False)  # e.g., Client_products_cache
    maxcache = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)  # Optional field
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<APIRoute(id={self.id}, method={self.method}, path={self.path})>"
    
    
    