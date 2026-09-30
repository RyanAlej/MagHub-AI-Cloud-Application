# HANDLES HTTP REQUESTS

# fastAPI routes between python functions like load balancer/manager
from fastapi import FastAPI

# StreamingResponse = sends data to the browser gradually instead of all at once
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    QuestionRequest, 
    ConversationResponse, 
    ChatSessionResponse, 
    ChatSession, 
    RenameChatRequest
)

from backend.ai_service import (
    ask_openai, 
    get_history, 
    delete_history, 
    get_conversation, 
    get_chat_sessions,
    get_chat,
    get_or_create,
    identify_VA_code_section
)

from backend.database import create_tables, SessionLocal

import json

from backend.retrieve_knowledge import retrieve_knowledge

# creates fastAPI application object
# runs in RAM, not the server
# when typing uvicorn backend.main:app this means...
# go into backend/main.py and find the variable named app, now Uvicorn has FastAPI object
app = FastAPI()

frontend_path = Path(__file__).parent.parent / "frontend"

app.mount(

    "/static",
    StaticFiles(directory=frontend_path),
    name="static"
)

# enable CORS so browsers allow the frontend to sent HTTP requests to this backend
# allow the front end (JS) to communicate with this FastAPI backend through the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    # allows JS to read the chat ID and RAG sources from the response headers
    expose_headers=["X-Chat-Id", "X-Sources"],
)

create_tables()

# AWS status endpoint
@app.get("/status")
def get_status():
    return {"status": "ok"}


# this is calling a URL. so https://127.0.0.10/ or https://127.0.0.10/ask, etc.
# one HTTP request --> one database session
# this creates an API endpoint in the backend and offers to the frontend
@app.get("/")
def home():
    return FileResponse(frontend_path / "index.html")


@app.post("/ask")
# QuestionRequest is question: str. so request now contains the object which contains question: "how are you?"
# fastAPI takes the ask_ai value (question: "how are you?"). 
def ask_ai(request: QuestionRequest):
    print(request.chat_id)

    chat_id = get_or_create(

        request.question,
        request.chat_id
    )

    # retrieve the knowledge chunks related to the user's question
    knowledge_results = retrieve_knowledge(request.question)

    retrieved_sources = []

    # go through each chunk that RAG retrieved
    for knowledge_chunk in knowledge_results:

        # store the PDF's name and official URL together
        source = {

            "name": knowledge_chunk.source_name,
            "url": knowledge_chunk.source_url
        }

        # only add this field guide PDF if I have not already added it
        if source not in retrieved_sources:
            retrieved_sources.append(source)

    # ask the helper to identify the relevant VA code section from the user's question
    sectionNumber = identify_VA_code_section(request.question)

    # if the identify_VA_Code_section returns a value which is 18.2-32 for example, this if runs
    if sectionNumber:

        titleNumber = sectionNumber.split("-"[0])

        virginiaCodeUrl = (

            f"https://law.lis.virginia.gov/vacode/"
            f"title{titleNumber}/section{sectionNumber}/"
        )

        retrieved_sources.append({

            "name": f"Virginia Code - § {sectionNumber}",
            "url": virginiaCodeUrl
        })

    # sends each yielded AI text chunk to the browser as it arrives
    return StreamingResponse(

        ask_openai(
            request.question,
            chat_id
        ),

        # tells the browser the streamed data is plain text
        media_type="text/plain",

        headers={

            "X-Chat-Id": str(chat_id),

            # convert the python source list into JSON text and send it to the browser
            "X-Sources": json.dumps(retrieved_sources)
        }
    )

# if someone sends a GET request to /history, run the function below
# response_model is from FastAPI library
# list[ConversationResponse] = expect a Python list where each item is a ConversationResponse
    # ConversationResponse = one conversation
    # list[ConversationResponse] = many conversations
@app.get("/history", response_model=list[ConversationResponse])
def history():
    return get_history()


# @app... is called a decorator. it means the function below me has this property. NOT A BLOCK
@app.delete("/history")
def delete():
    return delete_history()


@app.get("/chat-sessions", response_model=list[ChatSessionResponse])
def chat_sessions():
    return get_chat_sessions()

@app.get("/chat-sessions/{chat_id}")
def get_chat_by_id(chat_id: int):

    # this calls the get_chat function AND returns its value which is the chat_id
    return get_chat(chat_id)


@app.patch("/chat-sessions/{chat_id}")
def rename_chat(chat_id: int, request: RenameChatRequest):

    db = SessionLocal()

    try: 
        current_chat = (

            db.query(ChatSession)
            .filter(ChatSession.id == chat_id)
            .first()
        )

        if current_chat is None:
            return {"message": "Chat not found."}

        current_chat.title = request.title

        db.commit()

        return {"message": "Chat renamed successfully."}

    finally:
        db.close()


@app.delete("/chat-sessions/{chat_id}")
def delete_chat(chat_id: int):

    db = SessionLocal()

    try: 

        current_chat = (
                   
            db.query(ChatSession)
                    
            .filter(ChatSession.id == chat_id)
                    
            .first()
        )

        if current_chat is None:
            return {"message": "Chat not found."}

        db.delete(current_chat)

        db.commit()

        return {"message": "Chat deleted."}

    finally: 

        db.close()

    