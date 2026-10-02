# TALKS TO OPENAI

from backend.config import client

# starts conversation with PostgreSQL
from backend.database import SessionLocal

# importing the Conversation class
from backend.models import Conversation, ChatSession

from backend.retrieve_knowledge import retrieve_knowledge

from typing import Optional

from backend.retrieve_VA_code import retrieve_VA_code

def get_or_create(question: str, chat_id: Optional[int] = None):

    db = SessionLocal()

    try: 

        # look inside the chat_sessions table and give me the first row
        # current_chat = db.query(ChatSession).first()
            
        if chat_id is None:
            current_chat = ChatSession(
            
                title="New Chat"
            )
            
            db.add(current_chat)
            db.commit()
            db.refresh(current_chat)
            
            title = generate_chat_title(question)
                        
            current_chat.title = title
                        
            db.commit()
            
        else: 
            
            current_chat = (
                # look in the chat_sessions table
                db.query(ChatSession)
                # .filter() keep only rows matching this condition
                # ChatSession.id == chat_id = where the row's id equals chat_id the frontend sent
                .filter(ChatSession.id == chat_id)
                # give me the first (and only) matching row
                .first()
            )

        return current_chat.id

    finally:
        db.close()


def identify_VA_code_section(question):

    # ask the AI which VA code section most likely applies
    # this comes from openAI 
    response = client.responses.create(

        model="gpt-5.5",
        input=f"""
        Identify the Code of Virginia Section most likely relevant to this question.

        Question:
        {question}

        Return only the section number, such as:
        18.2-58

        If you cannot identify a section with reasonable confidence, return:
        NONE 
        """
    )

    # get the section number the AI returned
    sectionNumber = response.output_text.strip()

    # no reliable section was identified
    if sectionNumber == "NONE":
        return None

    return sectionNumber
        

def ask_openai(question: str, chat_id: Optional[int] = None):

    # creates database session object CONNECTION. opens a conversation with PostgreSQL
    # the session object has add(), commit(), close()
    db = SessionLocal()

    # calls the get_or_create function and takes the current_chat.id return
        # chat_id = get_or_create(question, chat_id)

    current_chat = (

        db.query(ChatSession)
        .filter(ChatSession.id == chat_id)
        .first()
    )

    try:

        history = (

            db.query(Conversation)
            .filter(Conversation.chat == current_chat)
            .all()
        )

        conversation_history = ""

        for convo in history:
            conversation_history += f"User: {convo.question}\n"
            conversation_history += f"Assistant: {convo.answer}\n"

        # call the retrieval function and sae what it returns
        knowledge_results = retrieve_knowledge(question)

        # build the retrieved knowledge context
        knowledge_context = ""

        for knowledge_chunk in knowledge_results:
            knowledge_context += f"Source: {knowledge_chunk.source_name}\n"
            knowledge_context += f"URL: {knowledge_chunk.source_url}\n"
            knowledge_context += f"Content: {knowledge_chunk.content}\n\n"

        # ask the AI which VA code section is relevant to the user's question
        sectionNumber = identify_VA_code_section(question)
        
        # start with no VA code text
        virginiaCode = None
        
        # if the AI identified a section, retrieve the current statute from VA LIS
        if sectionNumber:
        
            virginiaCode = retrieve_VA_code(sectionNumber)

        virginiaCodeContext = ""

        # if a VA code section was retrieved, add it to be the context for the final AI answer
        if virginiaCode:
            virginiaCodeContext = f"""

        Virginia Code Section: {sectionNumber}

        {virginiaCode}
        """
        # controls how MagHub structures and formats AI responses
        response_instructions = """

            You are MagHub, an AI assistant.

            Format responses using Markdown when it improves readability.

            Formatting rules:
            - Use headings to separate meaningful sections.
            - Use numbered lists when order, steps, or elements matter.
            - Use bullet lists for groups of related information.
            - Use Markdown tables when comparing information across clear categories.
            - Use horizontal dividers only when separating major sections.
            - Use fenced code blocks for multi-line code.
            - Use inline code for short code references such as variables, functions, commands, and file names.
            - Keep simple answers simple. Do not add unnecessary headings, tables, or sections.
            - Do not overuse bold text.

            Additional information and rules: 
            - When the user's question concerns a criminal offense, criminal procedure, or other legal issue governed by Virginia Law, identify the applicable Code of Virginia section(s) when available.
            - For criminal offenses, include the applicable Virginia Code section(s) and offense elements as a standard part of the response unless the user specifically requests otherwise.
            - When referring to a code section from Code of Virginia, always state the elements that apply for legality and validity.
            - Do not invent statutes, cases, facts, citations, or legal requirements.
            - Clearly state when information is uncertain or unavailable.
            - If a case is unfamiliar or possibly hard to decipher, refer to possible answers or additional options to help.
            - Do not assume missing facts. When important facts are missing, identify what additional information would help answer the question.
            - Distinguish between facts provided by the user and assumptions or inferences.
            - When multiple statutes or offenses may apply, identify the reasonable alternatives and explain the relevant distinctions.
            - When the answer depends on a factual determination, explain which facts are legally significant.
            - Do not treat an allegation as an established fact unless the user presents it as established.

            Response Style:
            - Be clear and concise, but provide enough detail to be useful.
            - Prefer direct explanations over unnecessary introductions.
            - Use plain language when possible.
            - Explain technical or legal terms when they may be unfamiliar.
            - Avoid repeating the user's question unless it helps clarify the answer.
            - Use bold text sparingly and only when emphasis materially improves readability.
            - Do not bold ordinary explanatory sentences, statutory text, or large portions of a response.
            - Prefer headings and spacing over excessive bold text for visual organization.
            - Answer the user's specific question directly and concisely.
            - Prioritize the most directly relevant retrieved information.
            - Offer suggestions or questions at the end of your response to help the user follow up.

            Legal source rules: 
            - For Virginia law questions, rely only on approved legal sources provided by MagHub.
            - Prefer the current Code of Virginia for statutory authority.
            - Use the Virginia Magistrate Field Guide for magistrate procedures and guidance.
            - Use approved Virginia court materials when applicable.
            - Do not invent or reconstruct statutory language from memory.
            - If the approved sources do not contain enough information to answer, say the available sources are insufficient.
            - Clearly identify the statute or source supporting the answer.
            - Clearly print the elements related to the code section listed if applicable.
            - Refer to Virginia Magistrate Field Guide when needed to assist in procedures and legal answers.
            - For Virginia legal questions, use the Retrieved Knowledge as the factual basis for any legal or procedural claims it supports.
            - Base legal claims on the retrieved sources and do not invent information that is not supported by them.
            - Use only source names, source URLs, and legal information provided in Retrieved Knowledge. Do not invent or modify citations.

            Analysis rules: 
            - Separate the applicable law from the application of the user's facts.
            - When analyzing an offense, evaluate the facts against each applicable element individually.
            - Identify which elements appear supported by the provided facts and which require additional information.
            - Identify conflicting or ambiguous facts and explain how they may affect the legal analysis.
            - Do not reach a legal conclusion when the available information is insufficient to support one.
            - When more than one reasonable legal interpretation exists, explain the alternatives rather than presenting one interpretation as certain.
            - When the user asks about a criminal offense, organize the response into clearly labeled major sections using Markdown level-two headings (`##`).
            - Include a separate `## Elements` section that lists the elements of the offense.
            - Include a separate `## Applicable Virginia Law` section identifying the applicable Code of Virginia section(s).
            - Keep statutory text separate from the Elements section. Do not substitute statutory text for a separate list of offense elements.

            Citation rules:
            - Place legal citations near the statement they support.
            - Clearly distinguish statutory authority from procedural guidance.
            - Identify the source by name and section when that information is available.
            - Never fabricate a citation, section number, quotation, or source.
            - If the exact supporting authority cannot be verified from the approved sources, state that clearly.
            - When citing a Code of Virginia section, identify the section number and provide the entire section verabtim clearly from the Code of Virginia source.
            - Clearly separate verbatim statutory text from MagHub's explanation or analysis.
            - If the code section is unusually long or contains multiple lengthy subsections and reproducing the entire section would substantially reduce readability, identify the applicable section and ask the user whether they want the entire section or only the relevant subsection(s).
            - Never silently omit portions of statutory text when presenting it as the entire code section.
        """

        prompt = (

            conversation_history
            + f"\nRetrieved Knowledge:\n{knowledge_context}"
            + f"\nVirginia Code:\n{virginiaCodeContext}"
            + f"\nUser: {question}\n"
            + "Assistant:"
        )


        # stores the complete AI answer as chunks arrive
        full_answer = ""

        # opens a streaming response so openAI sends the answer in pieces
        with client.responses.stream(

            model="gpt-5.5",
            instructions=response_instructions,
            input=prompt

        ) as stream:

        # it loops through each event from the OpenAI response stream. Each current event gets 
            # temporarily stored in event. Then we check whether that event contains a new piece of 
            # output text. If it does, we grab that text from event.delta

            # loops through each event openAI sends through the stream
            for event in stream:

                # only use events that contain a new piece of AI-generated text
                # openAI's SDK gives python an event object each time something happens in the stream
                # delta = the newest piece of text openAI just generated
                if event.type == "response.output_text.delta":

                    # take the text inside the event object and store in text_chunk variable
                    text_chunk = event.delta

                    # adds the newest piece to the complete answer
                    full_answer += text_chunk

                    # sends this piece outward immediately, then pauses until the next piece for the user
                    # yield = send a result, pause the function, then continue when next result available
                    yield text_chunk

        saved_answer = full_answer

        saved_source_names = set()

        if knowledge_results:

            saved_answer += "\n\n---\n\n**Sources:**\n"

            for knowledge_chunk in knowledge_results:

                if knowledge_chunk.source_name not in saved_source_names:

                    source_display_name = (

                        knowledge_chunk.source_name
                        .replace(".pdf", "")
                        .replace("chapter", "Chapter ")
                    )

                    saved_answer += (
                        f"\n\nMagistrate Field Guide - "
                        f"[{source_display_name}]({knowledge_chunk.source_url})"

                    )

                    saved_source_names.add(knowledge_chunk.source_name)

            if sectionNumber and virginiaCode:

                virginiaCodeUrl = f"https://law.lis.virginia.gov/vacode/title{sectionNumber.split('-')[0]}/section{sectionNumber}/"

                # sectionNumber = words you see
                # virginiaCodeUrl = website you go to
                saved_answer += f"\n\nVirginia Code - [§ {sectionNumber}]({virginiaCodeUrl})"

        # User: "How are you?"
        # Assistant: ...
        # PLUS all the conversation history from before

        # response = client.responses.create(

            # model="gpt-5.5",
            # input=prompt)

        # creates a python object that represents one row
        # sitting in python memory. PostgreSQL does not know it exists yet
        conversation = Conversation(

            # left side question = from the Conversation object --> question variable
            # right side question = use passed in question variable from the ask_openai function above
            chat=current_chat,
            question=question,
            answer=saved_answer
        )

        # adds but does not save
        db.add(conversation)

        # means save/permanently store this
        db.commit()


    except Exception as e:
        print(f"Error in ask_openai: {e}")
        raise

    # finally ALWAYS runs
    finally:
        db.close()


def get_history():
         # SQLAlchemy opened a connection (session) to PostgreSQL
         db = SessionLocal()

        # using my database session (db), query the Conversation table and return all rows as list
        # this is SQLAlchemy library 
        # queries the db and returns conversation ordered from highest ID to lowest ID
         history = db.query(Conversation).order_by(Conversation.id.desc()).all()

         db.close()

         return history


def get_chat_sessions():

    db = SessionLocal()

    chat_sessions = db.query(ChatSession).order_by(ChatSession.id.desc()).all()

    db.close()

    return chat_sessions


# return every conversation that belongs to the selected chat
def get_chat(chat_id: int):

    db = SessionLocal()

    conversations = db.query(Conversation).filter(

        # give me all Conversation rows where the chat_id column equals the chat_id passsed into this function
        Conversation.chat_id == chat_id

    # all() tells SQLAlchemy to run the query and give every matching row
    ).all()

    db.close()

    return conversations


# IMPORTANT*************************************************************

def delete_history():

    # create a new database session
    db = SessionLocal()

    try:
        # delete every row in the Conversation table
        db.query(Conversation).delete()

        # permanently save the deletion
        db.commit()

        # return a success message
        return {"message": "History deleted successfully."}

    # catch whatever error happened and store in variable e
    except Exception as e:

        # undo chagnes only if an error occurs
        db.rollback()

        # return the error message only not the error class
        # error class = ZeroDivisionError: 
        # error message string = division by zero
        return {"error": str(e)}

    finally: 
        # always close the db session
        db.close()


def get_conversation(conversation_id):
    db = SessionLocal()

    try: 
        # query the Conversation table for one row with the matching ID
        conversation = db.query(Conversation).filter(
             # compare the database ID to the passed-in ID
             Conversation.id == conversation_id
        # return the first matching row
        ).first()

        # return the conversation object
        return conversation

    finally:
         db.close()


def generate_chat_title(question):

    # client is your OpenAI connection with API key
    # responses is built in to OpenAI that handles AI requests
    response = client.responses.create(
        model="gpt-5.5",
        input=f"""
        generate a short chat title (2-5 words) for the following user question.

        This is a Virginia legal and magistrate application.
        Numbers formatted like 18.2-51, 19.2-82, 3.2-6570, or 8.01-428 should be interpreted as Virginia Code section numbers, not arithmetic.

        Question:
        {question}

        Only return the title. Do not include quotes or any explanation.
        """
    )
    return response.output_text