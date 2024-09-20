from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer

# Ensure NLTK resources are downloaded only if not already available
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

model = SentenceTransformer('all-mpnet-base-v2')
app = FastAPI()

class SearchResult(BaseModel):
    PageId: int
    FileName: str
    ContentType: str
    FilePath: str
    TextContent: str
    CosineSimilarity: float

# Database connection
def get_db_connection():
    return psycopg2.connect(
            dbname="UnifiedAppDb",
            user="postgres",
            password="YourStrong!Passw0rd",
            host="postgres",
            port="5432"
    )

# Function to query the database and retrieve results based on cosine similarity
@app.get("/search", response_model=List[SearchResult])
def search_documents(
    owner_id: str, 
    search_text: str,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Preprocess the search text before generating the embedding
        processed_text = preprocess_text(search_text)
        search_embedding = generate_embedding(processed_text)

        # Query with pgvector's cosine similarity
        cur.execute(""" 
            SELECT ds."PageId", 
                d."FileName", d."ContentType", d."FilePath", 
                ds."TextContent", 
                (ds."Embedding" <=> %s::vector) as "CosineSimilarity"
            FROM public."DocumentSegments" ds
            JOIN public."Documents" d ON ds."DocumentId" = d."Id"
            WHERE d."OwnerId" = %s
            ORDER BY "CosineSimilarity" ASC
            LIMIT %s OFFSET %s;
        """, (search_embedding, owner_id, page_size, (page_number - 1) * page_size))

        rows = cur.fetchall()
        results = []
        
        for row in rows:
            result = SearchResult(
                PageId=row[0],
                FileName=row[1],
                ContentType=row[2],
                FilePath=row[3],
                TextContent=row[4],
                CosineSimilarity=row[5]
            )
            results.append(result)
        
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()

def generate_embedding(text: str) -> list:
    try:
        return model.encode(text).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating embedding")

def preprocess_text(text: str) -> str:
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)
