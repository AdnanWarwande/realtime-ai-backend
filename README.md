# Realtime AI Backend

A simple, asynchronous backend for real-time AI conversations using WebSockets, Google Gemini, and Supabase.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file:
    ```ini
    GOOGLE_API_KEY=your_key_here
    GEMINI_MODEL=gemini-2.0-flash
    SUPABASE_URL=your_url
    SUPABASE_KEY=your_key
    ```

3.  **Database**:
    Run the SQL in `schema.sql` in your Supabase SQL Editor to create the necessary tables.

## Run

```bash
python main.py
```
Open [http://localhost:8000](http://localhost:8000) to chat.

## Structure

-   `main.py`: Application entry, WebSockets, and cleanup logic.
-   `ai.py`: Google Gemini LLM interaction.
-   `db.py`: Supabase database interaction.
-   `models.py`: Data models.

## Key Design Choices

I tried to keep things simple but powerful. Here's why I made these choices:

*   **Why FastAPI?**  
    It's built for speed and async Python. Since we need to handle WebSockets and streaming LLM tokens at the same time, FastAPI's async nature makes this trivial compared to older frameworks like Flask.

*   **Flat Structure**  
    You won't find deep folder trees here. I kept everything in the root (`main.py`, `ai.py`, `db.py`) because for a project this size, jumping between 10 different folders is just annoying. This way, you see exactly how the pieces fit together.

*   **Supabase for Speed**  
    Setting up a full Postgres server is a pain. Supabase gives us a real Postgres DB with a nice API out of the box. It let me focus on the Python code rather than database administration.

*   **The "Router" AI**  
    Instead of hardcoding "if user says weather", I gave the tools to Gemini and let it decide. It feels much more natural—the AI knows when it needs help (tools) and when it can just chat.
