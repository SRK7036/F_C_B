import os
import uuid
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import init_db, get_db, Lead, Session as DBSession, Message, Summary, Recommendation, Email
from schemas import LeadCreate, LeadCreateResponse, ChatRequest, ChatResponse, AgreeRequest, ExploreRequest
from emailer import send_confirmation_email
from rag.rag_agents import ask_rag

load_dotenv()
init_db()

app = FastAPI(title="LeadGen Agentic RAG API")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/leads/create", response_model=LeadCreateResponse)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        dob=payload.dob,
        zip_code=payload.zip_code,
        gender=payload.gender,
        address=payload.address,
        consent=payload.consent,
        status="in_chat",
    )
    db.add(lead)
    db.flush()

    token = str(uuid.uuid4())
    sess = DBSession(lead_id=lead.id, session_token=token)
    db.add(sess)
    db.commit()

    return LeadCreateResponse(session_token=token)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    sess = db.query(DBSession).filter(DBSession.session_token == req.session_token).first()
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid session.")

    db.add(Message(session_id=sess.id, role="user", content=req.message))
    sess.last_active_at = datetime.utcnow()
    db.commit()

    try:
        answer, sources = ask_rag(req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")

    db.add(Message(session_id=sess.id, role="assistant", content=answer))
    db.commit()

    return ChatResponse(response=answer)

@app.post("/actions/agree")
def agree(req: AgreeRequest, db: Session = Depends(get_db)):
    sess = db.query(DBSession).filter(DBSession.session_token == req.session_token).first()
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid session.")

    lead = db.query(Lead).filter(Lead.id == sess.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    rec = Recommendation(session_id=sess.id, plan_name="Selected Plan", reasoning="User agreed to proceed.")
    db.add(rec)

    lead.status = "agreed"

    sent = send_confirmation_email(lead.email, lead.full_name)
    db.add(Email(lead_id=lead.id, template="confirm", status="sent" if sent else "failed"))

    db.commit()
    return {"ok": True}

@app.post("/actions/explore")
def explore(req: ExploreRequest, db: Session = Depends(get_db)):
    sess = db.query(DBSession).filter(DBSession.session_token == req.session_token).first()
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid session.")

    db.add(Message(session_id=sess.id, role="user", content=f"Explore more: {req.preferences}"))
    db.commit()

    chat_history = db.query(Message).filter(Message.session_id == sess.id).order_by(Message.created_at).all()
    answer, _ = ask_rag(f"User preferences changed: {req.preferences}. Suggest an alternative.", chat_history)
    db.add(Message(session_id=sess.id, role="assistant", content=answer))
    db.commit()

    return {"response": answer}
