"""
Configuration settings for the chat application.

In Python, triple-quoted strings like this are called 'docstrings'.
They document what a module/function/class does (like XML comments in C#).
"""

import os  # Standard library for operating system operations

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# The Hugging Face model to use for chat
# DialoGPT-medium is a conversational AI model (~774MB download on first run)
MODEL_NAME: str = "microsoft/DialoGPT-medium"

# Maximum length of generated responses (in tokens, roughly ~4 chars per token)
MAX_LENGTH: int = 1000

# =============================================================================
# PYTHON CONCEPTS DEMONSTRATED HERE:
# =============================================================================
#
# 1. TYPE HINTS (: str, : int)
#    - Like C# static typing, but OPTIONAL in Python
#    - Python is dynamically typed, hints are for documentation/IDE support
#    - MODEL_NAME: str = "..." is like: public string ModelName = "...";
#
# 2. CONSTANTS
#    - Python has no 'const' keyword
#    - Convention: UPPERCASE_WITH_UNDERSCORES means "don't modify this"
#    - It's a social contract, not enforced by the language
#
# 3. os.getenv() - Reading environment variables
#    - Like Environment.GetEnvironmentVariable() in C#
#
# =============================================================================

# Optional: Hugging Face API token (only needed for private/gated models)
# Set this in your environment: $env:HF_TOKEN = "your_token_here"
HF_TOKEN: str | None = os.getenv("HF_TOKEN")

# The | None syntax is Python 3.10+ for "nullable"
# It's like: public string? HfToken in C#


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Database connection string for SQLAlchemy
# Format: "dialect+driver://username:password@host:port/database"
#
# For SQLite (file-based, no server needed):
#   "sqlite:///filename.db"  - Creates a file in current directory
#   "sqlite:////absolute/path/to/file.db"  - Absolute path (note: 4 slashes!)
#
# Compare to C# connection strings:
#   SQLite:     "Data Source=chat_history.db"
#   SQL Server: "Server=localhost;Database=MyDb;..."
#
# The three slashes (///) mean: "local file, relative path"
DATABASE_URL: str = "sqlite:///chat_history.db"

# =============================================================================
# FUTURE: If you want to switch databases, just change DATABASE_URL!
# =============================================================================
#
# PostgreSQL: "postgresql://user:password@localhost:5432/dbname"
# MySQL:      "mysql+pymysql://user:password@localhost:3306/dbname"
# SQL Server: "mssql+pyodbc://user:password@localhost/dbname?driver=ODBC+Driver+17"
#
# SQLAlchemy abstracts the differences - your Python code stays the same!
# This is just like how EF Core lets you switch between SQL Server/SQLite/etc.
# =============================================================================
