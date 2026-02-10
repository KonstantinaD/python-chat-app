"""
Main application entry point with Gradio UI.

Gradio is a Python library that creates web UIs for ML models.
Think of it like Blazor, but specifically designed for AI demos.
"""

import gradio as gr  # 'as gr' creates an alias (like 'using gr = Gradio;')

import chat_service  # Our business logic module

# =============================================================================
# THE CHAT FUNCTION (Called by Gradio on each user message)
# =============================================================================

def chat(message: str, history: list[tuple[str, str]]) -> str:
    """
    Handle a chat message and return a response.
    
    Gradio's ChatInterface calls this function automatically when
    the user sends a message. It passes:
    - message: The new message from the user
    - history: All previous (user, assistant) message pairs
    
    ---
    PYTHON CONCEPT: This is a 'callback function'
    
    We're passing this function to ChatInterface, which will call it later.
    Like passing an Action<string, List<...>> delegate in C#.
    In Python, functions are 'first-class citizens' - they can be passed around.
    """
    return chat_service.get_response(message, history)


# =============================================================================
# CREATE THE GRADIO INTERFACE
# =============================================================================

demo = gr.ChatInterface(
    fn=chat,  # The function to call (our callback)
    title="🤖 Python Chat App",
    description="A conversational AI powered by Hugging Face DialoGPT",
    examples=[
        "Hello! How are you today?",
        "Tell me a joke",
        "What's your favorite color?",
        "Can you help me learn Python?",
    ],
    theme="soft",  # Visual theme (try: "default", "soft", "glass")
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

if __name__ == "__main__":
    """
    This block only runs when you execute this file directly:
        python app.py
    
    It does NOT run when another file imports this module:
        import app  # This would NOT trigger the block below
    
    ---
    PYTHON CONCEPT: __name__ == "__main__"
    
    Every Python file has a special __name__ variable:
    - When run directly: __name__ = "__main__"
    - When imported: __name__ = "app" (the module name)
    
    This is like checking if you're in Program.Main() vs being used as a library.
    
    Why double underscores? They're called 'dunder' (double-under) methods.
    They indicate special Python behavior. Like [SpecialName] in .NET.
    """
    
    print("\n" + "=" * 60)
    print("Starting Chat Application...")
    print("=" * 60)
    print("\nOnce started, open your browser to: http://127.0.0.1:7860")
    print("Press Ctrl+C to stop the server\n")
    
    # Launch the Gradio web server
    demo.launch(
        server_name="127.0.0.1",  # localhost only (use "0.0.0.0" for network access)
        server_port=7860,          # Default Gradio port
        share=False,               # Set True to create a public URL (tunneled)
    )
