#!/bin/bash
# tyFlow Chatbot POC - Full Pipeline Runner

set -e  # Exit on error

echo "============================================================"
echo "🤖 tyFlow Documentation Chatbot POC"
echo "============================================================"
echo ""

# Check API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set"
    echo "Please set it in .env file or export it:"
    echo "  export OPENAI_API_KEY='sk-...'"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set"
    echo "Please set it in .env file or export it:"
    echo "  export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

echo "✓ API keys found"
echo ""

# Step 1: Crawl (if needed)
if [ ! -f "data/operators/mapping.json" ] || [ ! -f "data/operators/birth.json" ]; then
    echo "📄 Step 1: Crawling documentation..."
    cd crawler
    python poc_crawler.py
    cd ..
    echo ""
else
    echo "✓ Step 1: Crawled data already exists (skipping)"
    echo ""
fi

# Step 2: Index
echo "🔢 Step 2: Building index..."
cd indexer
python build_index.py
cd ..
echo ""

# Step 3: Chatbot
echo "💬 Step 3: Testing chatbot..."
cd bot
python chatbot.py
cd ..
echo ""

echo "============================================================"
echo "✅ POC Complete!"
echo "============================================================"
