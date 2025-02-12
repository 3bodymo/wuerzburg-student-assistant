from typing import List, Tuple
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from app.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Apartment, Place, WhatsAppGroup, Insurance, GeneralInfo, Bank, TelecomProvider, UsefulApp
import json
import os

settings = get_settings()

class RAGService:
    def __init__(self) -> None:
        """
        Initialize the RAG service with necessary components.

        Sets up embeddings, vector store, database connection, and loads general info.
        No parameters required as it uses environment settings.

        Returns:
            None
        """
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        self.vector_store = None
        self.qa_chain = None
        self.db_engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.db_engine)
        self._initialize_vector_store()
        with open(settings.GENERAL_INFO_PATH, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _get_db_content(self) -> List[dict]:
        """
        Fetch and format all database content for RAG processing.

        Retrieves data from all database tables and formats it into documents
        suitable for vector storage.

        Returns:
            List[dict]: List of formatted documents with the following structure:
                - text (str): The formatted content of the document
                - source (str): The table name source of the document
                - id (int): The unique identifier of the record
        """
        db = self.SessionLocal()
        try:
            # Fetch data from all tables
            apartments = db.query(Apartment).all()
            places = db.query(Place).all()
            whatsapp_groups = db.query(WhatsAppGroup).all()
            insurances = db.query(Insurance).all()
            general_info = db.query(GeneralInfo).all()
            banks = db.query(Bank).all()
            telecom_providers = db.query(TelecomProvider).all()
            useful_apps = db.query(UsefulApp).all()

            documents = []
            
            # Format apartment data
            for apt in apartments:
                doc = f"Apartment: {apt.title}\nLocation: {apt.address}\n"
                doc += f"Details: {apt.rooms} rooms, {apt.size}m², Rent: €{apt.price}\n"
                doc += f"Description: {apt.details_link}\n"
                documents.append({"text": doc, "source": "apartments", "id": apt.id})

            # Format places data
            for place in places:
                doc = f"Place: {place.name}\nType: {place.category}\n"
                doc += f"Location: {place.address}\n"
                doc += f"Price Range: {place.price_range}, Rating: {place.rating}\n"
                doc += f"Description: {place.description}"
                documents.append({"text": doc, "source": "places", "id": place.id})

            # Format WhatsApp groups data
            for group in whatsapp_groups:
                doc = f"WhatsApp Group: {group.name}\nCategory: {group.category}\n"
                doc += f"Description: {group.description}\nInvite Link: {group.invite_link}"
                documents.append({"text": doc, "source": "whatsapp_groups", "id": group.id})

            # Format insurance data
            for insurance in insurances:
                doc = f"Insurance: {insurance.company_name}\nCategory: {insurance.category}\n"
                doc += f"Description: {insurance.description}\nWebsite: {insurance.company_url}"
                documents.append({"text": doc, "source": "insurances", "id": insurance.id})

            # Format general info data
            for info in general_info:
                doc = f"General Info: {info.title}\nCategory: {info.category}\n"
                doc += f"Description: {info.description}"
                documents.append({"text": doc, "source": "general_info", "id": info.id})

            # Format bank data
            for bank in banks:
                doc = f"Bank: {bank.name}\n"
                doc += f"Description: {bank.description}\nWebsite: {bank.website_url}\n"
                doc += f"Free Student Plan Available: {bank.free_student_plan_available}"
                documents.append({"text": doc, "source": "banks", "id": bank.id})

            # Format telecom provider data
            for provider in telecom_providers:
                doc = f"Telecom Provider: {provider.name}\n"
                doc += f"Description: {provider.description}\nWebsite: {provider.website_url}"
                documents.append({"text": doc, "source": "telecom_providers", "id": provider.id})

            # Format useful app data
            for app in useful_apps:
                doc = f"Useful App: {app.name}\nCategory: {app.category}\n"
                doc += f"Description: {app.description}\nApp Store URL: {app.app_store_url}\n"
                doc += f"Play Store URL: {app.play_store_url}"
                documents.append({"text": doc, "source": "useful_apps", "id": app.id})

            return documents
        finally:
            db.close()

    def _initialize_vector_store(self) -> None:
        """
        Initialize or load the FAISS vector store.

        Checks for existing vector store and loads it, or creates a new one
        from database content if none exists. Also initializes the QA chain.

        Returns:
            None
        """
        faiss_path = settings.VECTOR_STORE_PATH
        
        # Check if FAISS index already exists
        if os.path.exists(faiss_path) and os.path.isdir(faiss_path) and len(os.listdir(faiss_path)) > 0:
            # Load existing vector store
            self.vector_store = FAISS.load_local(faiss_path, self.embeddings)
        else:
            # Create new vector store from database content
            documents = self._get_db_content()
            
            if not documents:
                documents = [{"text": "No data available yet", "source": "empty", "id": 0}]
            
            texts = [doc["text"] for doc in documents]
            metadatas = [{"source": doc["source"], "id": doc["id"]} for doc in documents]
            
            self.vector_store = FAISS.from_texts(
                texts,
                self.embeddings,
                metadatas=metadatas
            )
            # Save the vector store
            os.makedirs(faiss_path, exist_ok=True)
            self.vector_store.save_local(faiss_path)
        
        # Initialize QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                temperature=settings.MODEL_TEMPERATURE,
                model_name=settings.OPENAI_CHAT_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            ),
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
        )


    def query(self, query: str) -> Tuple[str, List[str]]:
        """
        Process a query through the RAG system.

        Args:
            query (str): The user's question or query text
            category (str, optional): Category context for the query. Defaults to None.

        Returns:
            Tuple[str, List[str]]: A tuple containing:
                - str: The generated answer to the query
                - List[str]: List of source documents used for the answer
        """
        query = f"""{query}
        Please structure your response in a clear and readable way:
        - Use emojis where appropriate to make the text more engaging
        - Use simple bullet points (•) for lists if needed
        - Keep paragraphs short and well-organized
        - Put any links on their own separate lines without any special formatting
        - Don't use any special Markdown formatting or styling
        - Use plain text only
        """
        
        result = self.qa_chain({"query": query})
                
        # Get source documents
        docs = self.vector_store.similarity_search(query, k=3)
        sources = [doc.page_content for doc in docs]

        return result["result"], sources