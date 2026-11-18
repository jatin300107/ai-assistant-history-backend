from backend.models import User , Conversation , Message
from sqlmodel import Session
from fastapi import HTTPException
def create_conversation(title:str,user_id:int,db:Session):
    new_conversation = Conversation(title=title,user_id=user_id)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

def save_message(msg,sender,db : Session,conversation_id=None):

    conv = db.get(Conversation, conversation_id)
    if not conv:
        raise ValueError("Conversation not found")
    new_message = Message(content=msg, sender=sender, conversation_id=conversation_id)  
    db.add(conv)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_owned_conversation(db, conversation_id: int, user) -> Conversation:
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv