# OpenAI turns the user's question into an embedding
from openai import OpenAI

from backend.database import SessionLocal
from backend.models import KnowledgeChunk


client = OpenAI()

# find the most relevant knowledge chunks for the user's question
def retrieve_knowledge(question):

    # turn the user's question into an embedding
    embedding_response = client.embeddings.create(

        model="text-embedding-3-small",
        input=question
    )

    # get the embedding numbers from OpenAI's response
    question_embedding = embedding_response.data[0].embedding

    # open a connection to the db
    db = SessionLocal()

    # compare the question embedding against stored knowledge embeddings. find the 3 knowledge most similar
    results = (

        db.query(KnowledgeChunk)
        .order_by(KnowledgeChunk.embedding.cosine_distance(question_embedding))
        .limit(5)
        .all()
    )

    # close the db connection
    db.close()

    # give the matching chunks back to whatever called this function
    return results


# receive the user's question
# turn the question into embedding numbers
# pull those numbers from the OpenAI response
# open the database
# compare the question embedding to stored embeddings
# sort by closest meaning
# keep the top 3 matches
# run the search
# close the database
# return the 3 matches


###########################################################################################