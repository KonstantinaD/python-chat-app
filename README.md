---
title: Python Chat App
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
---

# 🤖 Python Chat App

A conversational AI chatbot powered by Hugging Face DialoGPT with chat history persistence.

## Features

- 💬 Natural conversation with DialoGPT-medium model
- 💾 Chat history saved to SQLite database
- 🎨 Clean Gradio interface

## Tech Stack

- **Frontend**: Gradio
- **AI Model**: Microsoft DialoGPT-medium
- **Database**: SQLite + SQLAlchemy
- **Backend**: Python

## Local Development

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. In `app.py`: comment out `demo.launch()` and uncomment the `if __name__ == "__main__":` block
6. Run: `python app.py`
7. Open http://127.0.0.1:7860

## Deploy to Hugging Face
Go to huggingface.co/new-space
Create a new Gradio Space
Upload these files:
app.py
chat_service.py
chat_repository.py
database.py
models.py
config.py
requirements.txt
README.md

Or use Git:
git clone https://huggingface.co/spaces/YOUR_USERNAME/your-space-name
# Copy your files in, then:
git add .
git commit -m "Initial commit"
git push
