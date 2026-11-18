from google import genai
import os 
from pydantic import BaseModel , Field
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from backend.models import Conversation, Message
from typing import Optional
from sqlmodel import select
from backend.ai_assitant.helper import create_conversation , save_message , get_owned_conversation
from backend.db import get_session

from backend.auth.utlis import get_current_user

load_dotenv()



ai_assistant = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


MODEL = "gemini-4-hydrogen" 
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))  

class ChatRequest(BaseModel):
    prompt: str
    conversation_id: Optional[int] = None

@ai_assistant.post("/chat")
def chat_with_ai(
    body: ChatRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_session),
):
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    if not body.conversation_id :
        conversation = create_conversation(
            title=body.prompt[:50], user_id=current_user.id, db=db
        )
    else:
        conversation = db.get(Conversation, body.conversation_id)
        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")

    save_message(msg=body.prompt, sender="user", db=db, conversation_id=conversation.id)

    rows = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.id.desc())
        .limit(20)
    ).all()
    history = [
        {"role": "model" if m.sender == "assistant" else "user",
         "parts": [{"text": m.content}]}
        for m in reversed(rows)
    ]

    try:
        result = client.models.generate_content(model=MODEL, contents=history)
        reply = result.text
    except Exception:
        raise HTTPException(status_code=502, detail="AI model request failed")

    save_message(msg=reply, sender="assistant", db=db, conversation_id=conversation.id)
    return {"response": reply, "conversation_id": conversation.id}

@ai_assistant.get('/conversation/{conversation_id}')
def get_conversation(conversation_id: int, current_user=Depends(get_current_user), db=Depends(get_session)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation :
        raise HTTPException(status_code=404, detail="Conversation not found")
    if  conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.id.asc())
    ).all()

    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [
                {"id": m.id, "sender": m.sender, "content": m.content, "created_at": m.created_at}
                for m in messages
            ],
        }
    }

@ai_assistant.get('/list/conversations/')
def list_conversations(current_user=Depends(get_current_user), db=Depends(get_session)):
    
    conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in conversations
        ]
    }


class RenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
@ai_assistant.patch("/conversations/{conversation_id}")
def rename_conversation(conversation_id: int, body: RenameRequest,
                        current_user=Depends(get_current_user), db=Depends(get_session)):
    conv = get_owned_conversation(db, conversation_id, current_user)
    conv.title = body.title
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@ai_assistant.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, current_user=Depends(get_current_user), db=Depends(get_session)):
    conv = get_owned_conversation(db, conversation_id, current_user)
    db.delete(conv)
    db.commit()
    return {"msg": "Conversation deleted successfully"}