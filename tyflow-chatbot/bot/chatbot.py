"""
POC Chatbot for tyFlow documentation
Uses LangGraph for retrieval + OpenAI ChatGPT for answer generation
"""
import os
import ssl
import httpx
from pathlib import Path
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


load_dotenv()

# Create custom HTTP client with disabled SSL verification for testing
http_client = httpx.Client(verify=False)


# Define the state
class ChatState(TypedDict):
    query: str
    retrieved_docs: list
    answer: str
    sources: list


class TyFlowChatbot:
    def __init__(self, collection_name="tyflow_all", qdrant_path="../indexer/qdrant_storage"):
        self.collection_name = collection_name
        self.qdrant_path = Path(qdrant_path)

        # Initialize embeddings with custom HTTP client
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )

        # Initialize Qdrant vectorstore
        self.client = QdrantClient(path=str(self.qdrant_path))
        self.vectorstore = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )

        # Initialize OpenAI ChatGPT with custom HTTP client
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )

        # Create answer prompt
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a tyFlow documentation assistant. Your task is to help users understand tyFlow operators and their parameters.

Answer format requirements:
1. **단계별 절차** (Step-by-step procedure as numbered list)
2. **핵심 파라미터** (Key parameters - use EXACT names from documentation)
3. **주의사항** (Important notes/warnings if mentioned)
4. **문서 링크** (Documentation links with anchors)

Important rules:
- Use EXACT parameter names from the documentation
- Include section headings when referencing specific rollouts
- Keep answers concise but complete
- If information is not in the context, say so clearly
- Always provide documentation links

Context from documentation:
{context}

User question: {query}

Answer in Korean:"""),
        ])

        # Build LangGraph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(ChatState)

        # Define nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve_node(self, state: ChatState) -> ChatState:
        """Retrieve relevant documents"""
        query = state["query"]
        print(f"\n🔍 Searching for: '{query}'")

        # Search with hybrid approach (similarity)
        results = self.vectorstore.similarity_search(query, k=5)

        print(f"✓ Found {len(results)} relevant sections")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('title', 'N/A')} - {doc.metadata.get('section_heading', 'N/A')}")

        state["retrieved_docs"] = results
        return state

    def _generate_node(self, state: ChatState) -> ChatState:
        """Generate answer using Claude"""
        query = state["query"]
        docs = state["retrieved_docs"]

        print(f"\n💭 Generating answer with Claude...")

        # Format context
        context_parts = []
        sources = []

        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            context_parts.append(
                f"[Source {i}] {metadata.get('title', 'Unknown')} - {metadata.get('section_heading', 'N/A')}\n"
                f"URL: {metadata.get('full_url', 'N/A')}\n"
                f"Content:\n{doc.page_content}\n"
            )

            sources.append({
                "title": metadata.get('title', 'Unknown'),
                "section": metadata.get('section_heading', 'N/A'),
                "url": metadata.get('full_url', 'N/A'),
                "params": metadata.get('params', [])
            })

        context = "\n---\n".join(context_parts)

        # Generate answer
        messages = self.answer_prompt.format_messages(context=context, query=query)
        response = self.llm.invoke(messages)

        answer = response.content
        state["answer"] = answer
        state["sources"] = sources

        print(f"✓ Answer generated ({len(answer)} chars)")

        return state

    def ask(self, query: str) -> dict:
        """Ask a question and get an answer"""
        print("=" * 60)
        print(f"❓ Question: {query}")
        print("=" * 60)

        # Run graph
        result = self.graph.invoke({"query": query})

        print("\n" + "=" * 60)
        print("✅ Answer ready!")
        print("=" * 60)

        return {
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    def print_answer(self, result: dict):
        """Pretty print answer"""
        print(f"\n📝 Answer:\n")
        print(result["answer"])
        print(f"\n\n📚 Sources:")
        for i, source in enumerate(result["sources"], 1):
            print(f"\n{i}. **{source['title']}** - {source['section']}")
            print(f"   🔗 {source['url']}")
            if source['params']:
                print(f"   📋 Parameters: {', '.join(source['params'][:5])}")


def main():
    """Run POC test"""
    print("=" * 60)
    print("🤖 tyFlow Documentation Chatbot POC (OpenAI)")
    print("=" * 60)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not found")
        print("Please set OPENAI_API_KEY in .env file")
        return False

    # Initialize chatbot
    chatbot = TyFlowChatbot(
        collection_name="tyflow_all",
        qdrant_path="../indexer/qdrant_storage"
    )

    # Test questions
    test_questions = [
        "Mapping에서 카메라 기반 UV 투영하려면 어떻게 해야 하나요?",
        "Birth와 Birth Flow의 차이점은 무엇인가요?"
    ]

    for question in test_questions:
        result = chatbot.ask(question)
        chatbot.print_answer(result)
        print("\n" + "=" * 80 + "\n")

    print("✅ POC test complete!")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
