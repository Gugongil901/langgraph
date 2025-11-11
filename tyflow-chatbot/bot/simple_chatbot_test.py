#!/usr/bin/env python3
"""
Simple chatbot test WITHOUT LangGraph to isolate the issue
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient

load_dotenv()

print("=" * 60)
print("🤖 Simple Chatbot Test (No LangGraph)")
print("=" * 60)

# Initialize components
print("\n1. Initializing embeddings...")
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
print("✓ Embeddings ready")

print("\n2. Initializing Qdrant...")
client = QdrantClient(path="../indexer/qdrant_storage")
vectorstore = Qdrant(
    client=client,
    collection_name="tyflow_all",
    embeddings=embeddings
)
print("✓ Vectorstore ready")

print("\n3. Initializing ChatGPT...")
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
print("✓ ChatGPT ready")

# Test query
query = "Mapping에서 카메라 기반 UV 투영하려면 어떻게 해야 하나요?"

print(f"\n4. Testing retrieval...")
print(f"   Query: {query}")
results = vectorstore.similarity_search(query, k=5)
print(f"✓ Found {len(results)} results")

for i, doc in enumerate(results, 1):
    print(f"  {i}. {doc.metadata.get('title', 'N/A')} - {doc.metadata.get('section_heading', 'N/A')}")

print(f"\n5. Testing answer generation...")
# Format context
context_parts = []
for i, doc in enumerate(results, 1):
    metadata = doc.metadata
    context_parts.append(
        f"[Source {i}] {metadata.get('title', 'Unknown')} - {metadata.get('section_heading', 'N/A')}\n"
        f"URL: {metadata.get('full_url', 'N/A')}\n"
        f"Content:\n{doc.page_content}\n"
    )

context = "\n---\n".join(context_parts)

# Create prompt
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a tyFlow documentation assistant.

Context from documentation:
{context}

User question: {query}

Answer in Korean with:
1. Step-by-step procedure
2. Key parameters (exact names)
3. Documentation links

Answer:"""),
])

messages = answer_prompt.format_messages(context=context, query=query)
response = llm.invoke(messages)

print(f"✓ Answer generated ({len(response.content)} chars)")
print("\n" + "=" * 60)
print("📝 Answer:")
print("=" * 60)
print(response.content)
print("=" * 60)
