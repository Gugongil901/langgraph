# tyFlow Chatbot POC - Quick Start

## 🎉 POC Status: Crawling Complete!

크롤링이 성공적으로 완료되었습니다! 2개의 문서 페이지가 수집되었습니다:
- ✅ Mapping operator (18 sections)
- ✅ Birth operator (6 sections)

## 📦 What's Been Built

```
tyflow-chatbot/
├── crawler/          ✅ 완료 - Mapping + Birth 페이지 크롤링
│   ├── poc_crawler.py
│   └── debug_crawler.py
├── indexer/          ⏳ 준비됨 - 임베딩 & 벡터 DB
│   └── build_index.py
├── bot/              ⏳ 준비됨 - LangGraph 챗봇
│   └── chatbot.py
└── data/operators/   ✅ 데이터 수집 완료
    ├── mapping.json  (15KB, 18 sections)
    └── birth.json    (3KB, 6 sections)
```

## 🔑 Next Steps: API Keys Required

인덱서와 챗봇을 실행하려면 API 키가 필요합니다.

### 1. API 키 설정

```bash
cd /home/user/langgraph/tyflow-chatbot

# .env 파일 생성
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-...    # OpenAI API key (임베딩용)
ANTHROPIC_API_KEY=sk-ant-...  # Anthropic API key (챗봇용)
EOF
```

### 2. 환경 변수 로드

```bash
export $(cat .env | xargs)
```

### 3. 전체 파이프라인 실행

```bash
chmod +x run_poc.sh
./run_poc.sh
```

또는 단계별 실행:

```bash
# Step 1: 크롤링 (이미 완료)
cd crawler && python poc_crawler.py && cd ..

# Step 2: 인덱싱
cd indexer && python build_index.py && cd ..

# Step 3: 챗봇 테스트
cd bot && python chatbot.py && cd ..
```

## 🧪 Test Questions

챗봇이 답변할 테스트 질문들:
1. "Mapping에서 카메라 기반 UV 투영하려면 어떻게 해야 하나요?"
2. "Birth와 Birth Flow의 차이점은 무엇인가요?"

## 📊 Expected Costs

- 임베딩 (OpenAI): ~$0.01 (2 페이지, ~20 chunks)
- 챗봇 (Claude): ~$0.05 (2개 질문)
- **Total: ~$0.06**

## 🔍 What Was Learned (크롤링 단계)

### 성공 요인:
1. ✅ `#body-inner` 컨테이너 식별
2. ✅ H2/H3/H4 섹션 구조 파싱
3. ✅ 파라미터 추출 ("Name: description" 패턴)
4. ✅ Gzip 압축 해제 (Accept-Encoding 자동 처리)

### 해결한 문제들:
1. 503 에러 (봇 탐지) → User-Agent 개선
2. Gzip 압축 → Accept-Encoding 헤더 제거
3. 섹션 파싱 → H4 태그 추가 인식
4. 파라미터 추출 → 정규표현식으로 "Name:" 패턴 추출

## 📈 Next Phase: Full Expansion

POC 검증 후 확장 계획:
1. 전체 Operators 카테고리 (~50 페이지)
2. Modifiers, FAQ 추가
3. Version History 통합
4. 자동 업데이트 스케줄러

## 🐛 Troubleshooting

**"Could not find #body-inner"**
→ Gzip 압축 문제. `Accept-Encoding` 헤더를 제거하고 requests가 자동으로 처리하도록 설정

**"503 Service Unavailable"**
→ 봇 탐지. User-Agent를 개선하고 요청 간격(2-5초)을 늘림

**"No API key found"**
→ .env 파일을 만들고 `export $(cat .env | xargs)` 실행

## 📝 Files Generated

```bash
# Crawled data
data/operators/mapping.json   # 18 sections, 12+ params
data/operators/birth.json     # 6 sections, 10+ params

# To be generated:
indexer/qdrant_storage/       # Vector DB (after indexing)
```

## 🚀 Ready to Continue?

API 키를 설정하고 `./run_poc.sh`를 실행하세요!
