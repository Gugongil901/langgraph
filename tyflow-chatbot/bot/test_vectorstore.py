#!/usr/bin/env python3
"""
Test Qdrant vectorstore with OpenAI embeddings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🧪 Testing Qdrant Vectorstore with OpenAI")
print("=" * 60)

# Test 1: Import and initialize embeddings
print("\n1️⃣ Testing OpenAI Embeddings initialization...")
try:
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✓ Embeddings initialized")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 2: Initialize Qdrant client
print("\n2️⃣ Testing Qdrant client...")
try:
    from qdrant_client import QdrantClient
    qdrant_path = Path("../indexer/qdrant_storage")
    client = QdrantClient(path=str(qdrant_path))
    print(f"✓ Qdrant client connected to {qdrant_path}")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 3: Initialize Qdrant vectorstore
print("\n3️⃣ Testing Qdrant vectorstore initialization...")
try:
    from langchain_community.vectorstores import Qdrant
    vectorstore = Qdrant(
        client=client,
        collection_name="tyflow_all",
        embeddings=embeddings
    )
    print("✓ Vectorstore initialized")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

# Test 4: Try to embed a simple query (without searching)
print("\n4️⃣ Testing direct embedding...")
try:
    test_query = "Birth operator"
    embedded = embeddings.embed_query(test_query)
    print(f"✓ Embedded query: {len(embedded)} dimensions")
except Exception as e:
    print(f"✗ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Try similarity search
print("\n5️⃣ Testing similarity search...")
try:
    results = vectorstore.similarity_search("Birth operator", k=2)
    print(f"✓ Found {len(results)} results")
    if results:
        print(f"   First result: {results[0].metadata.get('title', 'N/A')}")
except Exception as e:
    print(f"✗ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
