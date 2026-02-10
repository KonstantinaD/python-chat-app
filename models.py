"""
Database Models - SQLAlchemy ORM Definitions.

=============================================================================
WHAT IS SQLAlchemy?
=============================================================================

SQLAlchemy is Python's most popular ORM (Object-Relational Mapper).
It's like Entity Framework in C#/.NET!

    C#/Entity Framework          |    Python/SQLAlchemy
    -----------------------------|--------------------------------
    DbContext                    |    Session
    DbSet<T>                     |    session.query(T)
    [Table("Name")]              |    __tablename__ = "name"
    [Key]                        |    primary_key=True
    [Required]                   |    nullable=False
    [ForeignKey]                 |    ForeignKey("table.column")
    Navigation Properties        |    relationship()
    .Include()                   |    .options(joinedload())
    Migrations                   |    Alembic (separate package)

=============================================================================
KEY PYTHON CONCEPTS IN THIS FILE
=============================================================================

1. CLASSES (finally! 😄)
   - Python classes look different from C#
   - No 'public' keyword - everything is public by default
   - __init__ is the constructor (like public ClassName() in C#)

2. INHERITANCE
   - class Child(Parent): instead of class Child : Parent
   - SQLAlchemy models inherit from 'Base' (like inheriting from DbEntity)

3. CLASS VARIABLES vs INSTANCE VARIABLES
   - Variables defined directly in class body (like __tablename__) are CLASS variables
   - Variables assigned in __init__ with self.x are INSTANCE variables
   - SQLAlchemy columns are special - they're class variables but become instance vars

4. THE 'self' PARAMETER
   - Like 'this' in C#, but EXPLICIT (you must write it)
   - First parameter of every instance method
   - def method(self, arg): is like public void Method(arg)
"""

from datetime import datetime
from typing import Optional  # For nullable types

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

# =============================================================================
# BASE CLASS
# =============================================================================
#
# declarative_base() creates a base class that all our models inherit from.
# This is like having a base DbEntity class in Entity Framework.
#
# In C# terms:
#     public abstract class DbEntity { }  // All entities inherit from this
#
# SQLAlchemy uses this to know which classes are database tables.
# =============================================================================

Base = declarative_base()


# =============================================================================
# CHAT SESSION MODEL
# =============================================================================

class ChatSession(Base):
    """
    Represents a chat conversation session.
    
    In C# Entity Framework, this would look like:
    
        public class ChatSession
        {
            [Key]
            public int Id { get; set; }
            
            public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
            
            // Navigation property
            public virtual ICollection<ChatMessage> Messages { get; set; }
        }
    """
    
    # __tablename__ is a special SQLAlchemy attribute that sets the table name
    # Like [Table("chat_sessions")] attribute in C#
    __tablename__ = "chat_sessions"
    
    # -------------------------------------------------------------------------
    # COLUMN DEFINITIONS
    # -------------------------------------------------------------------------
    #
    # SQLAlchemy columns use Column() to define database columns.
    # The pattern is: column_name = Column(Type, constraints...)
    #
    # Compare to C# EF:
    #     [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    #     public int Id { get; set; }
    #
    # Becomes:
    #     id = Column(Integer, primary_key=True)
    # -------------------------------------------------------------------------
    
    id = Column(Integer, primary_key=True)  # Auto-increment by default in SQLite
    
    created_at = Column(
        DateTime, 
        default=datetime.utcnow,  # Default value (like = DateTime.UtcNow)
        nullable=False
    )
    
    # -------------------------------------------------------------------------
    # RELATIONSHIP (Navigation Property)
    # -------------------------------------------------------------------------
    #
    # This creates a navigation property to related ChatMessage objects.
    # 
    # In C# EF: public virtual ICollection<ChatMessage> Messages { get; set; }
    #
    # 'back_populates' creates a two-way relationship (like EF navigation props)
    # It means: "ChatMessage has a 'session' property that points back to me"
    # -------------------------------------------------------------------------
    
    messages = relationship(
        "ChatMessage",           # The related class name (as string to avoid circular imports)
        back_populates="session", # The property on ChatMessage that references this
        cascade="all, delete-orphan",  # Delete messages when session is deleted
        order_by="ChatMessage.timestamp"  # Always return messages in order
    )
    
    # -------------------------------------------------------------------------
    # __repr__ METHOD
    # -------------------------------------------------------------------------
    #
    # __repr__ is like overriding ToString() in C#
    # Called when you print() the object or need a string representation
    # The f"..." is an f-string (formatted string), like $"..." in C#
    # -------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, created_at={self.created_at})>"


# =============================================================================
# CHAT MESSAGE MODEL
# =============================================================================

class ChatMessage(Base):
    """
    Represents a single message exchange (user question + bot response).
    
    In C# Entity Framework:
    
        public class ChatMessage
        {
            [Key]
            public int Id { get; set; }
            
            [ForeignKey("Session")]
            public int SessionId { get; set; }
            
            [Required]
            public string UserMessage { get; set; }
            
            [Required]
            public string BotResponse { get; set; }
            
            public DateTime Timestamp { get; set; } = DateTime.UtcNow;
            
            // Navigation property
            public virtual ChatSession Session { get; set; }
        }
    """
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    
    # Foreign Key to ChatSession
    # ForeignKey("table_name.column_name") references the parent table
    session_id = Column(
        Integer, 
        ForeignKey("chat_sessions.id"),  # References chat_sessions.id
        nullable=False
    )
    
    # Text columns for the messages
    # Text is for longer strings (like nvarchar(max) in SQL Server)
    # String(255) would be like nvarchar(255)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    
    timestamp = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    
    # -------------------------------------------------------------------------
    # RELATIONSHIP (Navigation Property back to parent)
    # -------------------------------------------------------------------------
    #
    # This is the other side of the relationship.
    # In C#: public virtual ChatSession Session { get; set; }
    # -------------------------------------------------------------------------
    
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self) -> str:
        # Truncate long messages for readability (like string.Substring in C#)
        user_preview = self.user_message[:30] + "..." if len(self.user_message) > 30 else self.user_message
        return f"<ChatMessage(id={self.id}, user='{user_preview}')>"


# =============================================================================
# PYTHON NAMING CONVENTIONS (vs C#)
# =============================================================================
#
# C# Convention          |  Python Convention (PEP 8)
# -----------------------|----------------------------
# PascalCase classes     |  PascalCase classes ✓ (same!)
# PascalCase methods     |  snake_case methods
# PascalCase properties  |  snake_case attributes
# _privateField          |  _private_attribute (single underscore)
# SCREAMING_CASE const   |  SCREAMING_CASE const ✓ (same!)
#
# So: GetUserById() in C# → get_user_by_id() in Python
#     UserId property    → user_id attribute
#
# =============================================================================
