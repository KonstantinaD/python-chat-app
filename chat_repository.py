"""
Chat Repository - Data Access Layer for Chat Operations.

=============================================================================
THE REPOSITORY PATTERN
=============================================================================

This file follows the Repository Pattern - exactly like in C#!

In a C# project, you might have:

    public interface IChatRepository
    {
        ChatSession CreateSession();
        void SaveMessage(int sessionId, string userMsg, string botResponse);
        List<ChatMessage> GetSessionHistory(int sessionId);
    }

    public class ChatRepository : IChatRepository
    {
        private readonly AppDbContext _context;
        
        public ChatRepository(AppDbContext context)
        {
            _context = context;
        }
        
        // Implementation...
    }

In Python, we typically use FUNCTIONS instead of classes for simple cases.
This is more "Pythonic" - simpler, less boilerplate.

We CAN use classes if we need:
- Dependency injection
- Complex state management
- To satisfy an interface/protocol

But for a simple CRUD layer? Functions work great!

=============================================================================
WHY FUNCTIONS INSTEAD OF A CLASS?
=============================================================================

In Python, there's a saying: "Simple is better than complex."

Class-based (more like C#):
    repo = ChatRepository(session)
    repo.create_session()

Function-based (more Pythonic):
    create_session()

Functions are chosen here because:
1. No state to maintain between calls (we get session from get_session())
2. Simpler to test (just call the function)
3. Less boilerplate (no __init__, no self everywhere)
4. Each function is independent and focused

=============================================================================
"""

from typing import Optional

from database import get_session
from models import ChatSession, ChatMessage


def create_session() -> ChatSession:
    """
    Create a new chat session and return it.
    
    Returns:
        The newly created ChatSession with its ID populated.
    
    ---
    C# EQUIVALENT:
    
        public ChatSession CreateSession()
        {
            using (var context = new AppDbContext())
            {
                var session = new ChatSession();
                context.ChatSessions.Add(session);
                context.SaveChanges();
                return session;
            }
        }
    """
    with get_session() as db:
        # Create a new session object
        chat_session = ChatSession()
        
        # Add to the database session (like context.Add() in EF)
        db.add(chat_session)
        
        # Commit the transaction (like context.SaveChanges())
        db.commit()
        
        # Refresh to get the auto-generated ID
        # In EF, this happens automatically; SQLAlchemy needs explicit refresh
        db.refresh(chat_session)
        
        return chat_session


def save_message(
    session_id: int, 
    user_message: str, 
    bot_response: str
) -> ChatMessage:
    """
    Save a message exchange to the database.
    
    Args:
        session_id: The ID of the chat session
        user_message: What the user said
        bot_response: What the bot replied
    
    Returns:
        The saved ChatMessage object with ID populated.
    
    ---
    C# EQUIVALENT:
    
        public ChatMessage SaveMessage(int sessionId, string userMsg, string botResponse)
        {
            using (var context = new AppDbContext())
            {
                var message = new ChatMessage
                {
                    SessionId = sessionId,
                    UserMessage = userMsg,
                    BotResponse = botResponse
                };
                context.ChatMessages.Add(message);
                context.SaveChanges();
                return message;
            }
        }
    
    ---
    PYTHON CONCEPT: MULTI-LINE FUNCTION PARAMETERS
    
    When a function has many parameters, we can split them across lines:
    
        def save_message(
            session_id: int, 
            user_message: str, 
            bot_response: str
        ) -> ChatMessage:
    
    This is purely for readability - Python allows this because the
    opening parenthesis hasn't been closed yet.
    """
    with get_session() as db:
        message = ChatMessage(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message


def get_session_history(session_id: int) -> list[tuple[str, str]]:
    """
    Get all messages for a session as (user, bot) tuples.
    
    This returns the format that Gradio expects for chat history!
    
    Args:
        session_id: The ID of the chat session
    
    Returns:
        List of (user_message, bot_response) tuples, ordered by timestamp.
    
    ---
    C# EQUIVALENT:
    
        public List<(string User, string Bot)> GetSessionHistory(int sessionId)
        {
            using (var context = new AppDbContext())
            {
                return context.ChatMessages
                    .Where(m => m.SessionId == sessionId)
                    .OrderBy(m => m.Timestamp)
                    .Select(m => (m.UserMessage, m.BotResponse))
                    .ToList();
            }
        }
    
    ---
    PYTHON CONCEPTS:
    
    1. LIST COMPREHENSION
       [(x.a, x.b) for x in items] 
       
       This is Python's super-powered LINQ Select()!
       
       C# LINQ: items.Select(x => (x.A, x.B)).ToList()
       Python:  [(x.a, x.b) for x in items]
       
    2. QUERY SYNTAX
       SQLAlchemy's query API is similar to LINQ:
       
       C#:     context.Messages.Where(m => m.SessionId == id)
       Python: db.query(ChatMessage).filter(ChatMessage.session_id == id)
    """
    with get_session() as db:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
            .all()  # Execute query and get all results (like .ToList())
        )
        
        # Convert to list of tuples using list comprehension
        # This is the format Gradio needs for chat history
        return [(msg.user_message, msg.bot_response) for msg in messages]


def get_or_create_session(session_id: Optional[int] = None) -> ChatSession:
    """
    Get an existing session or create a new one.
    
    Args:
        session_id: Optional ID of existing session. If None, creates new.
    
    Returns:
        The ChatSession (existing or newly created).
    
    ---
    PYTHON CONCEPTS:
    
    1. OPTIONAL PARAMETERS WITH DEFAULT VALUES
       session_id: Optional[int] = None
       
       C# equivalent: int? sessionId = null
       
       Optional[int] means "int or None" (like nullable int)
       = None sets the default value
    
    2. TRUTHY/FALSY VALUES
       'if session_id:' checks if session_id is "truthy"
       
       In Python, these are "falsy" (evaluate to False):
       - None, 0, "", [], {}, False
       
       Everything else is "truthy"
       
       So 'if session_id:' means "if session_id is not None and not 0"
    """
    if session_id:
        with get_session() as db:
            # Try to find existing session
            existing = db.query(ChatSession).filter(
                ChatSession.id == session_id
            ).first()  # .first() returns one result or None (like .FirstOrDefault())
            
            if existing:
                return existing
    
    # No valid session_id or session not found - create new
    return create_session()


def get_all_sessions() -> list[ChatSession]:
    """
    Get all chat sessions (for displaying session list).
    
    Returns:
        List of all ChatSession objects, newest first.
    
    ---
    C# EQUIVALENT:
    
        public List<ChatSession> GetAllSessions()
        {
            using (var context = new AppDbContext())
            {
                return context.ChatSessions
                    .OrderByDescending(s => s.CreatedAt)
                    .ToList();
            }
        }
    """
    with get_session() as db:
        return (
            db.query(ChatSession)
            .order_by(ChatSession.created_at.desc())  # .desc() for descending
            .all()
        )


# =============================================================================
# PYTHON vs C# QUERY COMPARISON CHEAT SHEET
# =============================================================================
#
# C# LINQ                              | Python SQLAlchemy
# -------------------------------------|----------------------------------
# .Where(x => x.Id == 5)               | .filter(Model.id == 5)
# .OrderBy(x => x.Name)                | .order_by(Model.name)
# .OrderByDescending(x => x.Date)      | .order_by(Model.date.desc())
# .First()                             | .first() (returns None if empty)
# .FirstOrDefault()                    | .first() (same - returns None)
# .Single()                            | .one() (throws if not exactly 1)
# .SingleOrDefault()                   | .one_or_none()
# .ToList()                            | .all()
# .Count()                             | .count()
# .Any()                               | .first() is not None
# .Select(x => x.Name)                 | Use list comprehension after .all()
# .Include(x => x.Related)             | .options(joinedload(Model.related))
#
# =============================================================================
