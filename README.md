# Self-Learning AI Agent

A portfolio-ready local Python project demonstrating persistent memory and feedback-based adaptive response selection.

## One-click Windows start
1. Install Python 3.10 or newer and enable **Add Python to PATH** during installation.
2. Extract this ZIP.
3. Double-click `run_app.bat`.
4. The first launch creates a virtual environment and installs Streamlit automatically.

## Features
- Streamlit chat-style interface
- SQLite persistent memory
- Similarity-based memory retrieval
- Positive/negative feedback learning
- Learning dashboard
- Memory browser and reset control
- No API key required

## How learning works
Each interaction is saved in SQLite. For a new request, the agent compares keywords with previous interactions. Positively rated memories receive preference; negatively rated memories are ignored. This is an educational adaptive-memory agent rather than autonomous model retraining.
