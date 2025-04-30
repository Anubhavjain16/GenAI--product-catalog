from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Load product data
catalog_df = pd.read_csv("products.csv")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
descriptions = catalog_df['description'].tolist()
embeddings = model.encode(descriptions, show_progress_bar=True)

# FAISS index
index = faiss.IndexFlatL2(embeddings[0].shape[0])
index.add(embeddings)

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/products")
def get_products():
    return catalog_df[['product_id', 'name', 'price', 'description']].to_dict(orient="records")

@app.post("/search")
def search_products(request: QueryRequest):
    question_emb = model.encode([request.question])
    D, I = index.search(question_emb, k=5)
    results = catalog_df.iloc[I[0]][['product_id', 'name', 'price', 'description']]
    return results.to_dict(orient="records")

@app.post("/gen")
def answer_question(request: QueryRequest):
    context_df = pd.DataFrame(search_products(request))
    context = "\n".join([f"{row['name']} - Rs.{row['price']}: {row['description']}" for _, row in context_df.iterrows()])
    prompt = f"User asked: {request.question}\nRelevant Products:\n{context}\n\nAnswer:" 

    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return {"response": completion.choices[0].message.content.strip()}
