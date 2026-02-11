"""
Main application entry point with Gradio UI.

Gradio is a Python library that creates web UIs for ML models.
Think of it like Blazor, but specifically designed for AI demos.
"""

import gradio as gr  # 'as gr' creates an alias (like 'using gr = Gradio;')

import chat_service  # Our business logic module
import chat_repository  # NEW: Data access for loading/saving chat history
from database import init_db  # NEW: Database initialization function

# =============================================================================
# 🌐 HUGGING FACE SPACES DEPLOYMENT
# =============================================================================
# When deployed to HF Spaces, the app is IMPORTED as a module (not run directly).
# This means __name__ == "__main__" block NEVER runs on Spaces!
# So we must initialize the database here, at module load time.
#
# This code runs in BOTH environments (local + deployed) - that's fine!
# init_db() is idempotent (safe to call multiple times).
# =============================================================================

print("Initializing Database...")
init_db()
print("Database ready!")

# =============================================================================
# THE CHAT FUNCTION (Called by Gradio on each user message)
# =============================================================================

def chat(message: str, history: list[tuple[str, str]], session_id: int) -> str:
    """
    Handle a chat message and return a response.
    
    Gradio's ChatInterface calls this function automatically when
    the user sends a message. It passes:
    - message: The new message from the user
    - history: All previous (user, assistant) message pairs
    - session_id: Our database session ID (passed via Gradio State)
    
    ---
    PYTHON CONCEPT: This is a 'callback function'
    
    We're passing this function to ChatInterface, which will call it later.
    Like passing an Action<string, List<...>> delegate in C#.
    In Python, functions are 'first-class citizens' - they can be passed around.
    
    ---
    NEW: We now use get_response_and_save() to persist messages!
    """
    return chat_service.get_response_and_save(message, history, session_id)


# =============================================================================
# CREATE THE GRADIO INTERFACE
# =============================================================================
#
# NEW: We use Gradio's 'State' feature to maintain a session_id per user.
# State is like storing data in session storage in a web app.
#
# How it works:
# 1. When a user opens the app, create_session_state() runs, creating a new
#    database session and returning its ID
# 2. This ID is stored in gr.State and passed to our chat() function
# 3. Each browser tab gets its own session (like separate users)
#
# In C#/Blazor terms:
#    @inject ProtectedSessionStorage SessionStorage
#    await SessionStorage.SetAsync("sessionId", newSessionId);
# =============================================================================

def create_session_state() -> int:
    """
    Create a new chat session in the database and return its ID.
    
    This is called once when a user opens the app (Gradio State initialization).
    
    Returns:
        The ID of the newly created session.
    
    ---
    This is like creating a new user session when someone opens your web app.
    The session_id is then stored in Gradio's State (like browser session storage).
    """
    session = chat_repository.create_session()
    print(f"Created new chat session with ID: {session.id}")
    return session.id


# Using Blocks for more control over the UI and state management
# Blocks is like having full control over your Blazor component layout
with gr.Blocks(theme="soft", title="🤖 Python Chat App") as demo:
    
    # -------------------------------------------------------------------------
    # gr.State - SESSION STORAGE
    # -------------------------------------------------------------------------
    #
    # gr.State stores data per-user-session (each browser tab is separate).
    # The 'value' parameter takes a FUNCTION that creates the initial value.
    #
    # IMPORTANT: We pass create_session_state (no parentheses!)
    # - create_session_state  = the function itself (called later by Gradio)
    # - create_session_state() = call it NOW and use the result (wrong!)
    #
    # This is like lazy initialization in C#:
    #     Lazy<int> sessionId = new Lazy<int>(() => CreateSession());
    # -------------------------------------------------------------------------
    
    session_state = gr.State(value=create_session_state)
    
    # UI Layout
    gr.Markdown("# 🤖 Python Chat App")
    gr.Markdown("A conversational AI powered by Hugging Face DialoGPT. Your chat history is now saved!")
    
    # -------------------------------------------------------------------------
    # ChatInterface with State
    # -------------------------------------------------------------------------
    #
    # 'additional_inputs' passes extra data to our chat function.
    # Every time a message is sent, Gradio calls:
    #     chat(message, history, session_state_value)
    #
    # This is how we get the session_id into our chat() function!
    # -------------------------------------------------------------------------
    
    chat_interface = gr.ChatInterface(
        fn=chat,
        examples=[
            "Hello! How are you today?",
            "Tell me a joke",
            "What's your favorite color?",
            "Can you help me learn Python?",
        ],
        additional_inputs=[session_state],  # Pass session ID to chat function
    )

# =============================================================================
# PYTHON CONCEPTS:
# =============================================================================
#
# 1. NAMED ARGUMENTS (fn=chat, title="...")
#    - Like C#: new ChatInterface(fn: chat, title: "...")
#    - Python uses = instead of :
#    - Order doesn't matter when using names
#
# 2. FUNCTIONS AS VALUES (fn=chat)
#    - We pass the function itself, not call it (no parentheses)
#    - fn=chat passes the function object
#    - fn=chat() would pass the RESULT of calling chat (wrong!)
#    - Like passing a delegate or Func<> in C#
#
# =============================================================================


# =============================================================================
# ENTRY POINT
# =============================================================================

# =============================================================================
# 🌐 HUGGING FACE SPACES DEPLOYMENT - AUTO LAUNCH
# =============================================================================
# When deployed to HF Spaces, Gradio auto-detects the 'demo' variable and
# launches it automatically. No explicit demo.launch() needed!
#
# HF Spaces runs this file as: import app (not python app.py)
# So __name__ == "app", not "__main__"
# =============================================================================

# Simplified launch for Hugging Face Spaces (comment out for local development)
demo.launch()

# =============================================================================
# 💻 LOCAL DEVELOPMENT - MANUAL LAUNCH
# =============================================================================
# Uncomment the block below and comment out demo.launch() above to run locally
# with custom server settings.
#
# To run locally: python app.py
# =============================================================================

# if __name__ == "__main__":
#     """
#     This block only runs when you execute this file directly:
#         python app.py
#     
#     It does NOT run when another file imports this module:
#         import app  # This would NOT trigger the block below
#     
#     ---
#     PYTHON CONCEPT: __name__ == "__main__"
#     
#     Every Python file has a special __name__ variable:
#     - When run directly: __name__ = "__main__"
#     - When imported: __name__ = "app" (the module name)
#     
#     This is like checking if you're in Program.Main() vs being used as a library.
#     """
#     
#     print("\n" + "=" * 60)
#     print("Starting Chat Application (LOCAL MODE)...")
#     print("=" * 60)
#     print("\nOnce started, open your browser to: http://127.0.0.1:7860")
#     print("Press Ctrl+C to stop the server")
#     print("\n💾 Chat history will be saved to: chat_history.db\n")
#     
#     # Launch the Gradio web server with LOCAL settings
#     demo.launch(
#         server_name="127.0.0.1",  # localhost only (use "0.0.0.0" for network access)
#         server_port=7860,          # Default Gradio port
#         share=False,               # Set True to create a public URL (tunneled)
#     )
