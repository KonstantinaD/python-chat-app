"""
Database Configuration and Session Management.

=============================================================================
THIS FILE IS LIKE YOUR DbContext SETUP IN C#
=============================================================================

In a typical C# project, you might have:

    // Program.cs or Startup.cs
    services.AddDbContext<AppDbContext>(options =>
        options.UseSqlite("Data Source=app.db"));

This file does the equivalent for SQLAlchemy:
1. Creates the database engine (connection)
2. Creates a session factory
3. Provides a function to initialize the database

=============================================================================
KEY CONCEPT: SESSIONS vs DbContext
=============================================================================

In Entity Framework:
    using (var context = new AppDbContext()) {
        context.Users.Add(user);
        context.SaveChanges();
    }

In SQLAlchemy:
    with get_session() as session:
        session.add(user)
        session.commit()

The Session is your 'unit of work' - it tracks changes and commits them.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import config  # Our config module with DATABASE_URL
from models import Base  # The base class that knows about all our models


# =============================================================================
# CREATE THE ENGINE
# =============================================================================
#
# The 'engine' is the core interface to the database.
# It manages database connections (like a connection pool).
#
# create_engine() is like:
#     SqliteConnection.CreateConnectionString(config.DATABASE_URL)
#
# IMPORTANT SQLite NOTES:
# - 'check_same_thread=False' allows SQLite to be used across threads
#   (SQLite normally restricts this for safety, but we need it for web apps)
# - 'echo=True' prints all SQL statements (great for learning! Turn off in prod)
# =============================================================================

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite in web apps
    echo=False  # Set to True to see all SQL queries (helpful for debugging!)
)

# =============================================================================
# CREATE SESSION FACTORY
# =============================================================================
#
# sessionmaker() creates a 'factory' that produces database sessions.
# It's like a Func<AppDbContext> in C# - a function that creates contexts.
#
# In C# DI terms:
#     services.AddScoped<AppDbContext>();  // Creates new context per request
#
# SessionLocal is a CLASS that, when instantiated, creates a new Session:
#     session = SessionLocal()  # Like: var context = new AppDbContext()
#
# autocommit=False: We manually call commit() (explicit transactions)
# autoflush=False:  We manually flush to DB (more control over when writes happen)
# =============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine  # Bind to our engine (database connection)
)


# =============================================================================
# CONTEXT MANAGER FOR SESSIONS
# =============================================================================
#
# This is a REALLY important Python pattern! Let me explain:
#
# In C#, you use 'using' for resource cleanup:
#     using (var context = new AppDbContext()) { ... }
#
# In Python, you use 'with' and 'context managers':
#     with get_session() as session: ...
#
# The @contextmanager decorator turns a function into a context manager.
# - Code before 'yield' runs when entering 'with' block (like constructor)
# - Code after 'yield' runs when exiting 'with' block (like Dispose())
#
# =============================================================================

@contextmanager
def get_session():
    """
    Provide a transactional scope around a series of operations.
    
    Usage:
        with get_session() as session:
            session.add(some_object)
            session.commit()
        # Session is automatically closed here, even if an error occurred
    
    This is equivalent to C#:
        using (var context = new AppDbContext()) {
            context.Add(someObject);
            context.SaveChanges();
        }
    
    ---
    PYTHON CONCEPTS:
    
    1. @contextmanager DECORATOR
       - Decorators modify functions (like C# attributes, but more powerful)
       - @contextmanager specifically makes functions usable with 'with'
    
    2. yield KEYWORD
       - Different from C# yield! (Python generators are their own topic)
       - Here, 'yield session' means "pause here, give this to the 'with' block"
       - When the 'with' block finishes, continue after yield
    
    3. try/finally
       - Works exactly like C# - finally always runs
       - Ensures session.close() happens even if there's an exception
    """
    session = SessionLocal()  # Create a new session
    try:
        yield session  # Give it to the 'with' block
    finally:
        session.close()  # Always close when done (like Dispose())


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db() -> None:
    """
    Create all database tables.
    
    This is like running 'Update-Database' or 'dotnet ef database update' in EF.
    
    Base.metadata.create_all() looks at all classes that inherit from Base
    and creates their tables if they don't exist.
    
    NOTE: This is simple for development. For production, you'd typically use
    Alembic (Python's migration tool, like EF Migrations) for proper versioning.
    """
    # Import models here to ensure they're registered with Base
    # (They were already imported at the top, but this makes it explicit)
    import models  # noqa: F401 (tells linters: yes, this import is intentional)
    
    Base.metadata.create_all(bind=engine)
    print("Database initialized! Tables created if they didn't exist.")


# =============================================================================
# PYTHON CONCEPTS SUMMARY
# =============================================================================
#
# 1. CONTEXT MANAGERS (with ... as ...)
#    - Python's equivalent to C# 'using' statements
#    - Ensures cleanup code runs (closing files, DB connections, etc.)
#    - You can create them with @contextmanager decorator
#
# 2. DECORATORS (@something)
#    - Functions that wrap other functions
#    - Like C# attributes, but they actually modify behavior at runtime
#    - Very common in Python: @property, @staticmethod, @contextmanager, etc.
#
# 3. yield IN CONTEXT MANAGERS
#    - Not the same as C#'s yield return!
#    - "Pause here, give this value out, resume when done"
#
# 4. FACTORY PATTERN
#    - SessionLocal is a factory - calling SessionLocal() creates new sessions
#    - Very common pattern in Python ORMs
#
# =============================================================================
