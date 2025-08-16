from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func, TypeDecorator, CHAR
import uuid

Base = declarative_base()

class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses Postgres UUID type, otherwise stores as CHAR(36)."""
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Import locally to avoid static import issues
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # type: ignore
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        return uuid.UUID(value)

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
