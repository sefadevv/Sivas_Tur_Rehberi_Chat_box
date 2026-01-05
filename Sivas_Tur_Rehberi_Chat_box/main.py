import os
import shutil
from typing import Dict
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.utilities import SerpAPIWrapper

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

app = FastAPI(title="SİVAS ŞEHİR REHBERİ")

llm = ChatOllama(model="gemma3:4b", temperature=0.3)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
search_tool = None
if SERPAPI_API_KEY:
    search_tool = SerpAPIWrapper(
        serpapi_api_key=SERPAPI_API_KEY, 
        params={"engine": "google", "gl": "tr", "hl": "tr"}
    )

_store: Dict[str, InMemoryChatMessageHistory] = {}
vector_db = None 

def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _store: _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen Sivas rehberisin. Samimi ve yardımsever ol."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chatbot = RunnableWithMessageHistory(prompt | llm, get_history, input_messages_key="input", history_messages_key="history")

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    res = chatbot.invoke({"input": request.message}, config={"configurable": {"session_id": request.session_id}})
    return ChatResponse(answer=res.content)

@app.post("/web_search", response_model=ChatResponse)
async def web_search(request: ChatRequest):
    if not search_tool: return ChatResponse(answer="API Key yok.")
    
    search_results = search_tool.run(request.message)
    
    rag_prompt = f"""
    Aşağıdaki Google arama sonuçlarını kullanarak kullanıcının sorusunu cevapla.
    Cevabın akıcı bir Sivas rehberi gibi olsun.
    
    Arama Sonuçları:
    {search_results}
    
    Kullanıcı Sorusu: {request.message}
    """
    ai_response = llm.invoke(rag_prompt)
    
    return ChatResponse(answer=ai_response.content)

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_db
    try:
        os.makedirs("temp_uploads", exist_ok=True)
        path = f"temp_uploads/{file.filename}"
        with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
        
        pages = PyPDFLoader(path).load()
        splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(pages)
        vector_db = FAISS.from_documents(splits, embeddings)
        
        os.remove(path)
        return {"status": "success", "message": "PDF Yüklendi! Artık soru sorabilirsin."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/ask_pdf", response_model=ChatResponse)
async def ask_pdf(request: ChatRequest):
    global vector_db
    if not vector_db: return ChatResponse(answer="⚠️ Lütfen önce PDF yükleyin.")
    
    docs = vector_db.similarity_search(request.message, k=3)
    context = "\n".join([d.page_content for d in docs])
    
    prompt = f"Doküman Bilgisi:\n{context}\n\nSoru: {request.message}"
    response = llm.invoke(prompt)
    
    return ChatResponse(answer=f"📄 **Doküman Cevabı:**\n{response.content}")