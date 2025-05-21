"""
Knowledge Agent with RAG capabilities for the Agent Swarm system.

This agent is responsible for handling queries that require information retrieval
and generation, particularly about InfinitePay products and services.
"""
from typing import Dict, Any, List, Optional
import os
import requests
from bs4 import BeautifulSoup
import re
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from .base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):
    """
    Knowledge Agent that uses RAG to answer queries about InfinitePay and general knowledge.
    
    This agent is responsible for retrieving information from the InfinitePay website
    and using it to answer user queries.
    """
    
    def __init__(self, name: str = "Knowledge", api_key: str = None):
        """Initialize the Knowledge Agent.
        
        Args:
            name: The name of the agent
            api_key: OpenAI API key for embeddings and LLM
        """
        super().__init__(name)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.infinitepay_urls = [
            "https://www.infinitepay.io",
            "https://www.infinitepay.io/maquininha",
            "https://www.infinitepay.io/maquininha-celular",
            "https://www.infinitepay.io/tap-to-pay",
            "https://www.infinitepay.io/pdv",
            "https://www.infinitepay.io/receba-na-hora",
            "https://www.infinitepay.io/gestao-de-cobranca-2",
            "https://www.infinitepay.io/gestao-de-cobranca",
            "https://www.infinitepay.io/link-de-pagamento",
            "https://www.infinitepay.io/loja-online",
            "https://www.infinitepay.io/boleto",
            "https://www.infinitepay.io/conta-digital",
            "https://www.infinitepay.io/conta-pj",
            "https://www.infinitepay.io/pix",
            "https://www.infinitepay.io/pix-parcelado",
            "https://www.infinitepay.io/emprestimo",
            "https://www.infinitepay.io/cartao",
            "https://www.infinitepay.io/rendimento"
        ]
        self.vectorstore = None
        self.qa_chain = None
        
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message by retrieving relevant information and generating a response.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            context: Optional context information
            
        Returns:
            Dict containing the response and any additional information
        """
        # Ensure the vectorstore is initialized
        if self.vectorstore is None:
            await self._initialize_rag_pipeline()
        
        # Check if this is a general knowledge question that might require web search
        if self._is_general_knowledge_question(message):
            response = await self._handle_general_knowledge(message)
        else:
            # Use RAG to answer the question
            response = await self._retrieve_and_generate(message)
        
        return {
            "response": response,
            "agent_type": "knowledge"
        }
    
    async def _initialize_rag_pipeline(self) -> None:
        """Initialize the RAG pipeline by scraping the InfinitePay website and creating a vectorstore."""
        # Record this operation
        self.record_tool_call("initialize_rag", {"status": "starting"})
        
        # Load documents from the InfinitePay website
        documents = []
        for url in self.infinitepay_urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
                self.record_tool_call("web_scraping", {"url": url, "status": "success"})
            except Exception as e:
                self.record_tool_call("web_scraping", {"url": url, "status": "error", "error": str(e)})
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Create vectorstore
        embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.vectorstore = FAISS.from_documents(splits, embeddings)
        
        # Create QA chain
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            api_key=self.api_key
        )
        
        template = """You are a helpful assistant for InfinitePay, a financial services company in Brazil.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        {context}
        
        Question: {question}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": prompt}
        )
        
        self.record_tool_call("initialize_rag", {"status": "completed"})
    
    def _is_general_knowledge_question(self, message: str) -> bool:
        """Determine if a message is asking for general knowledge rather than InfinitePay-specific info.
        
        Args:
            message: The user message to analyze
            
        Returns:
            True if the message is asking for general knowledge, False otherwise
        """
        # Convert message to lowercase for easier pattern matching
        message_lower = message.lower()
        
        # Check for InfinitePay mentions
        infinitepay_patterns = [
            r"infinitepay",
            r"infinite pay",
            r"maquininha",
            r"card machine",
            r"card reader",
            r"tap to pay",
            r"pix",
            r"boleto",
            r"conta digital",
            r"digital account",
            r"emprestimo",
            r"loan",
            r"cartao",
            r"card"
        ]
        
        for pattern in infinitepay_patterns:
            if re.search(pattern, message_lower):
                return False
        
        # Check for general knowledge patterns
        general_patterns = [
            r"(news|information) (about|on|regarding)",
            r"(latest|recent) (news|information|updates)",
            r"weather",
            r"sports",
            r"politics",
            r"entertainment",
            r"technology",
            r"science",
            r"health",
            r"education",
            r"business",
            r"economy",
            r"stock market",
            r"cryptocurrency"
        ]
        
        for pattern in general_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Default to False (assume InfinitePay-related)
        return False
    
    async def _handle_general_knowledge(self, message: str) -> str:
        """Handle general knowledge questions using web search.
        
        Args:
            message: The user message to process
            
        Returns:
            Response string
        """
        # Record this operation
        self.record_tool_call("web_search", {"query": message})
        
        # For this implementation, we'll use a simulated web search response
        # In a real implementation, this would use a search API or web scraping
        
        response = (
            "I found some information that might help answer your question. "
            "However, as I'm primarily designed to provide information about InfinitePay's "
            "products and services, I may not have the most up-to-date or comprehensive "
            "information on general topics. "
            "For the most accurate and current information, I recommend consulting a dedicated "
            "search engine or relevant authoritative sources."
        )
        
        return response
    
    async def _retrieve_and_generate(self, message: str) -> str:
        """Use RAG to retrieve relevant information and generate a response.
        
        Args:
            message: The user message to process
            
        Returns:
            Response string
        """
        # Record this operation
        self.record_tool_call("rag_query", {"query": message})
        
        try:
            # Run the query through the QA chain
            result = self.qa_chain.invoke({"query": message})
            response = result.get("result", "")
            
            # If response is empty or indicates no information, provide a fallback
            if not response or "don't know" in response.lower() or "don't have" in response.lower():
                response = (
                    "I don't have specific information about that in my knowledge base. "
                    "For the most accurate and up-to-date information about InfinitePay's "
                    "products and services, I recommend visiting their official website at "
                    "https://www.infinitepay.io or contacting their customer support directly."
                )
            
            return response
        except Exception as e:
            self.record_tool_call("rag_error", {"error": str(e)})
            return (
                "I'm having trouble retrieving the information you requested. "
                "Please try again later or contact InfinitePay's customer support "
                "for assistance with your query."
            )
