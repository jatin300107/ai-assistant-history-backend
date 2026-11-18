# ai-assistant-history-backend

FastAPI backend for an AI assistant's chat history: JWT auth, per-user conversations and messages, and Gemini replies.

## Stack
Python, FastAPI, SQLModel, SQLite, bcrypt, JWT, Gemini API

## Run locally
```bash
git clone https://github.com/jatin300107/ai-assistant-history-backend.git
cd ai-assistant-history-backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
uvicorn backend.app:app --reload
```

Environment variables (see `.env.example`):
- `GOOGLE_API_KEY`
- `SECRET_KEY`
- `DB_URL`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

API docs are at `http://127.0.0.1:8000/docs` once it's running.

## Endpoints
| Method | Route | What it does |
|---|---|---|
| POST | `/auth/register` | Create a user (password stored as a bcrypt hash) |
| POST | `/auth/login` | Returns a JWT |
| POST | `/ai-assistant/chat` | Send a prompt. Creates a conversation if no `conversation_id` is given, saves both messages, returns the Gemini reply |
| GET | `/ai-assistant/list/conversations/` | List the current user's conversations, newest activity first |
| GET | `/ai-assistant/conversation/{conversation_id}` | Get one conversation with its messages |
| PATCH | `/ai-assistant/conversations/{conversation_id}` | Rename a conversation |
| DELETE | `/ai-assistant/conversations/{conversation_id}` | Delete a conversation and its messages |

## How history is handled
- Three tables: `users`, `conversations`, `messages`. Each message stores a `sender` of `user` or `assistant`.
- Every conversation endpoint checks ownership. Another user's conversation returns 404, so IDs can't be probed.
- `/ai-assistant/chat` saves the user's message first, sends the last 20 messages to Gemini as context, then saves the reply. If the model call fails, the user's message is not lost.
- A conversation's `updated_at` changes with each new message, so the list stays ordered by recent activity.

## Not built
Refresh tokens, rate limiting and automated tests.