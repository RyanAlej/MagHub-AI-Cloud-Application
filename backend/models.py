# DEFINES THE DATA (THE REQUEST BODY)

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

from typing import Optional

# base model is a pydantic library class. gives your class auto data validation, parsing, & JSON conversion
# pydantic is a python library that validates, parses, and converts data into python objects
# from pydantic = library
# import BaseModel = class inside that library
from pydantic import BaseModel

from pgvector.sqlalchemy import Vector


# this expects data from the user
class QuestionRequest(BaseModel):
    # every request should have a field called question, and it must be a string
    question: str

    chat_id: Optional[int] = None

# QuestionRequest = your own class that represents what data you expect from the user
# BaseModel = Pydantic's class that gives your class the ability to auto convert and validate JSON

# need jSON input? --> use a BaseModel
# need JSON output? --> Return a dictionary or BaseModel


class RenameChatRequest(BaseModel):
    title: str


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


# this will send data back to the user
class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str


class ChatSessionResponse(BaseModel):
    id: int
    title: str


class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )


# DEFINING THE SCHEMA OF THE TABLE

# conversation inherits from Base
class Conversation(Base):
    # when you create this model in PostgreSQL, name the table conversations
    __tablename__ = "conversations"

    # id = the column name
    # Mapped[int] = this column stores integers
    # mapped_column(...) = tells SQLAlchemy "this is a database column"
    # primary_key=True = every row gets a unique ID
    id: Mapped[int] = mapped_column(primary_key=True)

    # Create a column named chat_id. This column is a foreign key that points to the id column in the chat_sessions table
        # chat_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE")
    )

    chat: Mapped["ChatSession"] = relationship(

        back_populates="conversations"
    )

    # question = column name
    # Mapped[str] = column stores Python strings
    # mapped_column(String) = tells SQLAlchemy to create a PostgreSQL TEXT/VARCHAR-type column
    question: Mapped[str] = mapped_column(String)

    answer: Mapped[str] = mapped_column(String)


class KnowledgeChunk(Base):

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)

    # store the numeric embedding for this text chunk so pgvector can compare its meaning to user questions
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))


class VirginiaCodeSection(Base):

    __tablename__ = "VA_code_sections"

    # creates unique db ID for each row
    id: Mapped[int] = mapped_column(primary_key=True)

    # VA code section number, such as 18.2-51
    section_number: Mapped[str] = mapped_column(String, unique=True)

    # VA section title/description 
    section_title_and_description: Mapped[str] = mapped_column(Text)