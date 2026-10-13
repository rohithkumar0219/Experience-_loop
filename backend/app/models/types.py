import uuid
from sqlalchemy.types import TypeDecorator, CHAR, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, INET as PG_INET


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


def JSONBType():
    """Returns JSONB for PostgreSQL and JSON for other dialects like SQLite."""
    return PG_JSONB().with_variant(JSON(), "sqlite")


def INETType():
    """Returns INET for PostgreSQL and String(45) for other dialects."""
    return PG_INET().with_variant(String(45), "sqlite")


def EnumType(enum_cls, name: str):
    """Returns PostgreSQL native ENUM on PostgreSQL, and VARCHAR with CHECK on SQLite."""
    from sqlalchemy import Enum as SAEnum
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda obj: [e.value for e in obj],
        validate_strings=True,
        create_type=True
    )
