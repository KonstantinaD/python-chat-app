"""
Chat Service - Handles interaction with the Hugging Face model.

This is the 'business logic' layer. In Python, we often use FUNCTIONS
instead of classes when there's no complex state to manage.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

import config  # Import our config module (like 'using MyApp.Config;' in C#)
import chat_repository  # NEW: Our data access layer for persistence

# =============================================================================
# MODULE-LEVEL INITIALIZATION
# =============================================================================
#
# In Python, code at the module level runs ONCE when the module is first imported.
# This is like a static constructor in C#, or code in Program.cs.
#
# We load the model here so it's ready when chat requests come in.
# Loading a model takes 10-30 seconds, so we only want to do it once.
# =============================================================================

print(f"Loading model: {config.MODEL_NAME}...")
print("(This may take a minute on first run - the model will be downloaded)")

# Tokenizer: Converts text to numbers (tokens) that the model understands
# Like a translator between human text and AI-readable format
tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)

# Model: The actual AI brain that generates responses
model = AutoModelForCausalLM.from_pretrained(config.MODEL_NAME)

print("Model loaded successfully!")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def get_response(message: str, history: list[tuple[str, str]]) -> str:
    """
    Generate a response to the user's message.
    
    Args:
        message: The user's input text
        history: List of previous (user_message, bot_response) tuples
                 This is how Gradio passes chat history
    
    Returns:
        The AI's response as a string
    
    ---
    PYTHON CONCEPTS:
    
    1. FUNCTION DEFINITION
       def function_name(param: Type) -> ReturnType:
       
       Like C#: public string GetResponse(string message, List<...> history)
    
    2. DOCSTRINGS IN FUNCTIONS
       The triple-quoted string right after 'def' documents the function.
       Shows up in IDE tooltips, like XML docs in C#.
    
    3. TYPE HINTS FOR COMPLEX TYPES
       list[tuple[str, str]] means: List<(string, string)> in C#
       - list[X] = List<X>
       - tuple[A, B] = (A, B) value tuple
    """
    
    # Build conversation context from history
    # We need to format previous messages so the model remembers the conversation
    conversation_history = ""
    
    for user_msg, bot_msg in history:  # Tuple unpacking (like C# deconstruction)
        conversation_history += f"{user_msg}{tokenizer.eos_token}{bot_msg}{tokenizer.eos_token}"
    
    # Add the new user message
    conversation_history += f"{message}{tokenizer.eos_token}"
    
    # =============================================================================
    # ENCODING: Convert text to token IDs (numbers)
    # =============================================================================
    input_ids = tokenizer.encode(conversation_history, return_tensors="pt")
    # return_tensors="pt" means return a PyTorch tensor (the format the model needs)
    
    # =============================================================================
    # GENERATION: Let the model predict the next tokens
    # =============================================================================
    output_ids = model.generate(
        input_ids,
        max_length=config.MAX_LENGTH,
        pad_token_id=tokenizer.eos_token_id,  # Prevents a warning
        do_sample=True,           # Add randomness (not always same response)
        top_p=0.92,               # Nucleus sampling (quality control)
        top_k=50,                 # Limit vocabulary choices
        temperature=0.7,          # Lower = more focused, higher = more creative
    )
    
    # =============================================================================
    # DECODING: Convert token IDs back to text
    # =============================================================================
    # We only want the NEW tokens (the response), not the input echoed back
    # input_ids.shape[1] gives us the length of the input
    new_tokens = output_ids[:, input_ids.shape[1]:]
    
    response = tokenizer.decode(new_tokens[0], skip_special_tokens=True)
    
    return response


def get_response_and_save(
    message: str, 
    history: list[tuple[str, str]], 
    session_id: int
) -> str:
    """
    Generate a response AND save it to the database.
    
    This wraps get_response() and adds persistence.
    
    Args:
        message: The user's input text
        history: List of previous (user_message, bot_response) tuples
        session_id: The ID of the chat session to save to
    
    Returns:
        The AI's response as a string
    
    ---
    PYTHON CONCEPT: FUNCTION COMPOSITION
    
    This function composes (combines) two operations:
    1. Generate response (get_response)
    2. Save to database (chat_repository.save_message)
    
    This is a common pattern - build complex operations from simpler ones.
    In C#, you might do this with method chaining or service composition.
    
    We keep get_response() separate so it can still be used without persistence
    (useful for testing or if someone wants to use the model without a database).
    """
    # Generate the response using the existing function
    response = get_response(message, history)
    
    # Save to database
    chat_repository.save_message(
        session_id=session_id,
        user_message=message,
        bot_response=response
    )
    
    return response


# =============================================================================
# PYTHON CONCEPTS SUMMARY:
# =============================================================================
#
# 1. f-STRINGS (f"Loading model: {config.MODEL_NAME}")
#    - Like $"Loading model: {config.ModelName}" in C#
#    - The 'f' prefix enables variable interpolation
#
# 2. IMPORTING MODULES
#    - 'import config' loads config.py as a module
#    - Access with dot notation: config.MODEL_NAME
#    - Like 'using' + namespace in C#, but more explicit
#
# 3. from X import Y
#    - Imports specific items from a module
#    - Like 'using static' or specific type imports in C#
#
# 4. TUPLE UNPACKING
#    for user_msg, bot_msg in history:
#    - Automatically splits each tuple into two variables
#    - Like: foreach (var (userMsg, botMsg) in history) in C#
#
# 5. SLICING (output_ids[:, input_ids.shape[1]:])
#    - Python's powerful array slicing syntax
#    - [start:end] extracts a portion
#    - [:, X:] means "all rows, columns from X onwards"
#    - No direct C# equivalent - LINQ would be more verbose
#
# =============================================================================
