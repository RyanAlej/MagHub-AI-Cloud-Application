from openai import OpenAI

from backend.database import SessionLocal
from backend.models import KnowledgeChunk

from pypdf import PdfReader
from pathlib import Path

client = OpenAI()

# create a path object pointing to the knowledge folder
knowledge_folder = Path("knowledge")

# find every file inside knowledge/ that ends in .pdf
# .glob() = method that searches that folder for matching filenames
pdf_files = knowledge_folder.glob("*.pdf")

db = SessionLocal()

# loop through the PDF files and temporarily store the current file in pdf_file
for pdf_file in pdf_files:

    # PdfReader() opens your PDF and creates a python object representing that PDF
    # "knowledge/toc.pdf" means to enter the knowledge folder, then find this PDF inside it
    pdf_reader = PdfReader(pdf_file)

    source_text = ""

    # .pages comes build into the PdfReader object; it contains the PDF's pages in order
    # "page" is a temporary variable I am creating here; each loop assigns the next PDF page to it
    for page in pdf_reader.pages:

        # .extract_text() is a pypdf method that reads the current page and returns its written text as a string
        # "\n" is a newline character, so text from the next PDF page starts on a new line
        source_text += page.extract_text() + "\n\n"

    # use the current PDF's filename as its source name
    source_name = pdf_file.name

    # create the offical VA courts URL by adding the current PDF filename to the Manual's base URL
    source_url = f"https://www.vacourts.gov/static/courtadmin/aoc/mag/resources/magman/{pdf_file.name}"

    # find the old chunks belonging to this PDF and delete them before adding fresh ones
    db.query(KnowledgeChunk).filter(

        KnowledgeChunk.source_name == source_name
    ).delete()

    # set how many characters of PDF text will go into each chunk
    # this is characters of english text 
    # 1536 is the number of embeddings
    # the 2000 is sent to openAI, then creates 1 embedding that has 1536 numbers from that 2000 chunk size
    chunk_size = 2000

    # range() creates starting positions 0, 2000, 4000, 6000... until it reaches the end of source_text
    # Loop 1 → start_position = 0
    # Loop 2 → start_position = 2000
    # Loop 3 → start_position = 4000
    # Loop 4 → start_position = 6000
    # every time this loops repeats, assign the NEXT number from the range to start_position
    for start_position in range(0, len(source_text), chunk_size):

        # take the text starting at start_position and stop 2000 characters later

        # start_position = 0
        # → grab source_text[0:2000]

        # start_position = 2000
        # → grab source_text[2000:4000]

        # start_position = 4000
        # → grab source_text[4000:6000]
        chunk_text = source_text[start_position:start_position + chunk_size]

        # send the current 2000-character chunk to OpenAI and ask for its embedding
        # client is openAI, so it is creating an embedding and storing in embedding_response
        embedding_response = client.embeddings.create(

            model="text-embedding-3-small",
            input=chunk_text
        )

        # pull the actual list of 1536 embedding numbers out of OpenAI's response
        # use openAI's embedding response variable that contains the model and input
        # .data is openAI tool that gets the returned embedding results
        # [0] gets the FIRST result
        # .embedding is openAI tool and gets its actualy 1536 number vector
        chunk_embedding = embedding_response.data[0].embedding

        # create a KnowledgeChunk object containing this chunk's source, text, and embedding
        # KnowledgeChunk is the SQLAlchemy model that defines the tables structure
        # knowledge_chunk_row is ONE row created using that structure
        knowledge_chunk_row = KnowledgeChunk(

            source_name=source_name,
            source_url=source_url,
            content=chunk_text,
            embedding=chunk_embedding
        )

        # add this chunk during each loop
        db.add(knowledge_chunk_row)

# only runs when the entire loop is finished
db.commit()
db.close()