"""
POC Indexer for tyFlow documentation
Loads crawled JSON, chunks sections, embeds, and stores in Qdrant
"""
import json
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


load_dotenv()


class TyFlowIndexer:
    def __init__(self, data_dir="../data", collection_name="tyflow_all"):
        self.data_dir = Path(data_dir)
        self.collection_name = collection_name

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize Qdrant path (client will be created by from_documents)
        self.qdrant_path = Path("./qdrant_storage")
        self.qdrant_path.mkdir(exist_ok=True)

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

    def load_documents(self) -> List[Document]:
        """Load all JSON files from data directory (including subdirectories)"""
        documents = []

        print(f"\n📂 Loading documents from {self.data_dir}")
        # Recursively find all JSON files in subdirectories
        json_files = list(self.data_dir.glob("**/*.json"))

        if not json_files:
            print(f"  ⚠ Warning: No JSON files found in {self.data_dir}")
            return []

        print(f"  Found {len(json_files)} JSON files")

        for json_file in json_files:
            print(f"  Loading {json_file.name}...")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create documents from sections
            for section in data.get('sections', []):
                content = section.get('content', '')
                if not content or len(content) < 50:  # Skip empty/tiny sections
                    continue

                # Build metadata
                metadata = {
                    'source': data['url'],
                    'title': data['title'],
                    'category': data.get('category', 'Unknown'),
                    'operator': data.get('operator', data['title']),
                    'section_heading': section.get('heading', ''),
                    'section_level': section.get('level', 'h2'),
                    'anchor': section.get('anchor', ''),
                    'params': section.get('params', []),
                    'crawled_at': data.get('crawled_at', '')
                }

                # Build full URL with anchor
                full_url = f"{data['url']}#{section['anchor']}" if section.get('anchor') else data['url']
                metadata['full_url'] = full_url

                doc = Document(
                    page_content=f"# {section['heading']}\n\n{content}",
                    metadata=metadata
                )
                documents.append(doc)

        print(f"✓ Loaded {len(documents)} sections from {len(json_files)} files")
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        print(f"\n✂️  Chunking documents...")

        chunks = []
        for doc in documents:
            # For short sections, keep as-is
            if len(doc.page_content) < 900:
                chunks.append(doc)
            else:
                # Split longer sections
                split_docs = self.text_splitter.split_documents([doc])
                chunks.extend(split_docs)

        print(f"✓ Created {len(chunks)} chunks from {len(documents)} sections")
        return chunks

    def create_collection(self, vector_size=1536):
        """Create Qdrant collection - not needed, from_documents handles it"""
        pass

    def index_documents(self, chunks: List[Document]):
        """Embed and store chunks in Qdrant"""
        print(f"\n🔢 Embedding and indexing {len(chunks)} chunks...")
        print(f"   ⏱️  This will take 10-15 minutes...")

        # Create vectorstore (will create its own client)
        vectorstore = Qdrant.from_documents(
            chunks,
            self.embeddings,
            path=str(self.qdrant_path),
            collection_name=self.collection_name,
            force_recreate=True
        )

        print(f"✓ Indexed {len(chunks)} chunks in Qdrant")
        return vectorstore

    def run_indexing(self):
        """Run full indexing pipeline"""
        print("=" * 60)
        print("🏗️  tyFlow Documentation Indexer")
        print("=" * 60)

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            print("\n❌ Error: OPENAI_API_KEY not found in environment")
            print("Please create a .env file with your OpenAI API key:")
            print("  OPENAI_API_KEY=sk-...")
            return False

        # Load documents
        documents = self.load_documents()
        if not documents:
            print("\n❌ No documents to index")
            return False

        # Chunk documents
        chunks = self.chunk_documents(documents)

        # Index in Qdrant
        vectorstore = self.index_documents(chunks)

        # Test search
        print("\n🔍 Testing search...")
        test_query = "How to use camera-based UV mapping?"
        results = vectorstore.similarity_search(test_query, k=2)

        print(f"\nTest query: '{test_query}'")
        print(f"Top result:")
        print(f"  - Title: {results[0].metadata.get('title', 'N/A')}")
        print(f"  - Section: {results[0].metadata.get('section_heading', 'N/A')}")
        print(f"  - URL: {results[0].metadata.get('full_url', 'N/A')}")
        print(f"  - Content preview: {results[0].page_content[:150]}...")

        print("\n" + "=" * 60)
        print("✅ Indexing complete!")
        print(f"📊 Collection: {self.collection_name}")
        print(f"📍 Storage: {self.qdrant_path}")
        print("=" * 60)

        return True


if __name__ == "__main__":
    # Index all categories
    indexer = TyFlowIndexer(data_dir="../data", collection_name="tyflow_all")
    success = indexer.run_indexing()
    exit(0 if success else 1)
