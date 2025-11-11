# tyFlow Documentation Chatbot POC

docs.tyflow.com 전용 검색형 챗봇 프로토타입

## 🎯 목표

tyFlow 문서에서 정확한 정보를 찾아 구조화된 답변을 제공:
- 단계별 절차
- 핵심 파라미터 (정확한 명칭)
- 문서 링크 (앵커 포함)

## 📦 구조

```
tyflow-chatbot/
├── crawler/          # 크롤러 (POC: Mapping + Birth 2개 페이지)
├── indexer/          # 인덱서 (청크 분할 + 임베딩 + Qdrant)
├── bot/              # 챗봇 (LangGraph + Claude)
├── data/             # 수집된 JSON 데이터
└── qa/               # 테스트 스크립트
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# API 키 설정
cp .env.example .env
# .env 파일을 열어서 API 키 입력:
# - OPENAI_API_KEY (임베딩용)
# - ANTHROPIC_API_KEY (Claude 챗봇용)
```

### 2. 의존성 설치

```bash
# 크롤러
cd crawler
pip install -r requirements.txt

# 인덱서
cd ../indexer
pip install -r requirements.txt

# 챗봇
cd ../bot
pip install -r requirements.txt
```

### 3. 실행

```bash
# Step 1: 크롤링 (Mapping + Birth 페이지)
cd crawler
python poc_crawler.py

# Step 2: 인덱싱 (청크 분할 + 임베딩)
cd ../indexer
python build_index.py

# Step 3: 챗봇 테스트
cd ../bot
python chatbot.py
```

## 📋 테스트 질문

1. "Mapping에서 카메라 기반 UV 투영하려면 어떻게 해야 하나요?"
2. "Birth와 Birth Flow의 차이점은 무엇인가요?"

## 🔍 POC 검증 항목

- [x] 크롤러: 페이지 수집 + HTML 파싱
- [x] 인덱서: 섹션 분할 + 임베딩 + Qdrant 저장
- [x] 챗봇: 검색 + Claude 답변 생성
- [ ] End-to-end 테스트 실행
- [ ] 답변 품질 검증 (링크, 파라미터 정확도)

## 🎓 기술 스택

- **크롤링**: requests + BeautifulSoup
- **임베딩**: OpenAI text-embedding-3-small
- **벡터 DB**: Qdrant (로컬)
- **챗봇**: LangGraph + Claude 3.5 Sonnet
- **언어**: Python 3.11+

## 📈 다음 단계

POC 성공 시:
1. 전체 Operators 카테고리 확장 (50-100 페이지)
2. Modifiers, FAQ 추가
3. Version History 통합 (최신 변경사항 자동 첨부)
4. 챗봇 UI 개선
5. 자동 업데이트 (주간 크롤링)

## ⚠️ 주의사항

- 크롤링 전 robots.txt 확인 필수
- 요청 간격 2초 (Be polite!)
- API 비용: 임베딩 ~$0.50, Claude 사용량 기반

## 📝 라이선스

교육/연구 목적. tyFlow 문서 저작권은 원 제작사에 있음.
