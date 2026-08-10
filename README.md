# 🎨 AI 브랜드 아이덴티티 생성기

브랜드 브리프(업종·타겟·키워드 등) 하나만 입력하면 **브랜드 네이밍 · 슬로건 · 스토리 · 컬러 팔레트 · 로고 시안**까지 AI가 자동으로 생성해 주는 CLI 프로그램입니다.

LLM API(OpenAI Chat Completions)로 텍스트 기반 브랜드 요소를 생성하고, 이미지 생성 API(`gpt-image-1`)로 로고 시안을 만든 뒤, 모든 결과물을 하나의 출력 폴더에 저장합니다.

---

## ✨ 주요 기능

| 단계 | 기능 | 설명 |
|------|------|------|
| 입력 | 브랜드 브리프 로드 | JSON 파일로 업종·타겟·키워드 등을 입력받고 필수 필드를 검증 |
| 1 | 브랜드 요소 생성 | 네이밍 후보 3~5개(의미 포함), 슬로건 3개, 스토리(300자 내외), 컬러 팔레트, 로고 프롬프트를 LLM으로 한 번에 생성 |
| 2 | 컬러 팔레트 시각화 | 메인/서브 HEX 컬러를 `matplotlib`으로 시각화하여 `color_palette.png`로 저장 |
| 3 | 로고 시안 생성 | 이미지 생성 API로 서로 다른 콘셉트의 로고 시안 2개를 PNG로 저장 |
| 4 | 결과 저장 | 모든 텍스트 결과를 `brand_result.json`으로 저장 |

### 보너스 기능
- **다국어 네이밍**: 한글 브랜드명(`name`)과 영문 브랜드명(`name_en`)을 동시에 생성
- **경쟁사 분석**: 브리프에 경쟁사가 있으면 차별화 포인트(`differentiation`)를 함께 제안

---

## 📁 프로젝트 구조

```
Project-A/
├── main.py               # CLI 진입점 · 전체 파이프라인 실행 · 컬러 팔레트 시각화 · 결과 저장
├── agent.py              # BrandAgent: LLM/이미지 API 호출, 프롬프트 생성, 응답 검증
├── requirements.txt      # 의존성 목록
├── .env                  # OPENAI_API_KEY (git 미추적)
├── briefs/               # 예시 브랜드 브리프 JSON
│   ├── brief_01_eco_cosmetics.json
│   ├── brief_02_premium_dessert_cafe.json
│   └── brief_03_senior_health_app.json
└── output/               # 생성 결과물 (git 미추적)
    ├── brand_result.json
    ├── color_palette.png
    ├── logo_01.png
    └── logo_02.png
```

---

## 🔧 요구 사항

- **Python 3.10 이상** (개발 환경: 3.12)
- OpenAI API 키 (텍스트 + 이미지 생성 권한 및 잔액 필요)

### 의존성
- `openai>=1.30.0` — LLM 및 이미지 생성 API
- `python-dotenv>=1.0.0` — `.env` 환경변수 로드
- `matplotlib>=3.8.0` — 컬러 팔레트 시각화

---

## 🚀 설치 및 실행

### 1. 가상환경 생성 및 의존성 설치

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API 키 설정

API 키는 코드에 직접 작성하지 않고 **환경변수 또는 `.env` 파일**에서 읽어옵니다.
프로젝트 루트에 `.env` 파일을 만들고 다음과 같이 작성하세요.

```
OPENAI_API_KEY=your_api_key_here
```

> `.env`는 `.gitignore`에 등록되어 있어 저장소에 커밋되지 않습니다.
> 터미널에서 `export OPENAI_API_KEY=...`로 직접 환경변수를 설정해도 됩니다.

### 3. 실행

```bash
python main.py
```

실행하면 대화형으로 브리프 파일 경로와 출력 폴더 경로를 입력받습니다.

---

## 💻 실행 예시

```
$ python main.py

🎨 AI 브랜드 아이덴티티 생성기
==================================================
브리프 파일 경로를 입력하세요: briefs/brief_01_eco_cosmetics.json
출력 폴더 경로를 입력하세요 (엔터 시 ./output):

[1/5] 브랜드 요소 생성 중...

  [네이밍]
    - 자연의 숨결 (Breath of Nature): 자연의 순수함과 생명력을 담아낸 브랜드명
    - 비건하모니 (Vegan Harmony): 비건과 조화를 뜻하는 브랜드명
    - 그린누리 (Green World): 친환경과 지속가능한 소비로 이루어진 세상

  [슬로건]
    - "자연의 힘으로, 당신의 아름다움을 지켜요."
    - "지속 가능한 아름다움, 비건으로 시작하세요."
    - "민감한 피부에, 순수한 자연을 담았습니다."

  [스토리] 생성 완료 (243자)

  [차별화 포인트]
    - 100% 자연 유래 성분만 사용하여 피부 안전성을 극대화
    - 지속 가능한 포장재 사용으로 환경 보호에 기여

[2/5] 컬러 팔레트 시각화 중...
  - 메인: #A8D8B9
  - 서브: #F0E3D2, #B5D99C, #7C9A61
  - 저장: ./output/color_palette.png

[3/5] 로고 시안 2개 생성 중...
  - 저장: ./output/logo_01.png
  - 저장: ./output/logo_02.png

[4/5] 전체 결과 JSON 저장 중...
  - 저장: ./output/brand_result.json

[5/5] 작업 완료!
✅ 완료! /경로/output 폴더를 확인하세요.
```

---

## 📥 입력: 브랜드 브리프 형식

JSON 파일로 브랜드 정보를 입력합니다.

| 필드 | 필수 | 타입 | 설명 |
|------|:----:|------|------|
| `industry` | ✅ | string | 업종 |
| `target` | ✅ | string | 타겟 고객 |
| `keywords` | ✅ | string[] | 핵심 키워드 (1개 이상) |
| `tone` | ⬜ | string | 톤앤매너 (기본값: "신뢰감 있고 대중적인") |
| `competitors` | ⬜ | string[] | 경쟁사 목록 |
| `notes` | ⬜ | string | 추가 요청사항 |

### 예시 (`briefs/brief_01_eco_cosmetics.json`)

```json
{
  "industry": "친환경 화장품",
  "target": "자연 유래 성분과 지속가능한 소비에 관심 있는 20~30대 여성",
  "keywords": ["비건", "자연 유래", "민감성 피부", "친환경"],
  "tone": "따뜻하고 신뢰감 있는",
  "competitors": ["이니스프리", "아로마티카"],
  "notes": "브랜드명은 한글과 영어를 함께 제안하고, 지속가능성과 자연 친화적인 이미지를 강조해 주세요."
}
```

---

## 📤 출력물

출력 폴더(기본값 `./output`)에 다음 파일이 저장됩니다.

| 파일 | 설명 |
|------|------|
| `brand_result.json` | 입력 브리프 + 생성된 모든 텍스트 결과(네이밍·슬로건·스토리·컬러·로고 프롬프트·차별화 포인트) |
| `color_palette.png` | 메인/서브 컬러 팔레트 시각화 이미지 |
| `logo_01.png`, `logo_02.png` | 로고 시안 이미지 |

### `brand_result.json` 구조

```json
{
  "brief": { "...입력 브리프 원본..." },
  "result": {
    "namings": [
      { "name": "자연의 숨결", "name_en": "Breath of Nature", "meaning": "..." }
    ],
    "slogans": ["...", "...", "..."],
    "story": "브랜드 스토리 내용...",
    "color_palette": { "main": "#A8D8B9", "sub": ["#F0E3D2", "#B5D99C", "#7C9A61"] },
    "logo_prompt": "A clean vector logo icon for...",
    "differentiation": ["...", "..."]
  }
}
```

---

## 🧩 동작 파이프라인

```
브리프 JSON ──▶ load_brief()          # 필수 필드 검증
             │
             ▼
      BrandAgent.generate_brand_elements()   # LLM 호출 → JSON 파싱 → 구조 검증
             │  (namings / slogans / story / color_palette / logo_prompt / differentiation)
             ▼
      save_color_palette()            # matplotlib으로 HEX 컬러 시각화 → PNG
             │
             ▼
      BrandAgent.generate_logo_image()   # 로고 프롬프트에 변주(variation) 추가 → 이미지 API → PNG
             │
             ▼
      brand_result.json 저장
```

- **텍스트 생성**: `agent.py`의 `build_prompt()`가 브리프를 구조화된 프롬프트로 변환하고, `response_format={"type": "json_object"}`로 JSON 응답을 강제한 뒤 `validate_result()`로 구조를 검증합니다.
- **로고 변주**: `main.py`의 `create_logo_variation_prompt()`가 동일한 브랜드 아이덴티티를 유지하면서 시안마다 다른 콘셉트(심볼 중심 / 워드마크 중심 등)를 부여합니다.
- **컬러 검증**: `is_valid_hex()`로 `#RRGGBB` 형식을 검증한 뒤에만 시각화합니다.

---

## 🛡️ 에러 처리

- **API 키 미설정/오류**: `BrandAgent` 초기화 시 명확한 안내 메시지를 출력하고 종료합니다.
- **단계별 실패 격리**: LLM 호출, 컬러 팔레트 생성, 개별 로고 생성 중 하나가 실패해도 프로그램 전체를 중단하지 않고 경고를 출력한 뒤 **다음 단계를 계속 진행**합니다.
- **입력 검증**: 브리프 파일 부재, JSON 형식 오류, 필수 필드 누락 등을 사전에 검증하여 친절한 오류 메시지를 제공합니다.

---

## 🔑 API 키 관리 정책

- API 키를 **코드에 하드코딩하지 않습니다.**
- `python-dotenv`로 `.env` 파일 또는 시스템 환경변수(`OPENAI_API_KEY`)에서 로드합니다.
- `.env`, `output/`, `.venv/`, `__pycache__/`는 `.gitignore`로 저장소에서 제외됩니다.

---

## ⚙️ 설정 값

`agent.py` / `main.py` 상단에서 조정할 수 있습니다.

| 항목 | 위치 | 기본값 |
|------|------|--------|
| 텍스트 모델 | `BrandAgent(text_model=...)` | `gpt-4o-mini` |
| 이미지 모델 | `BrandAgent(image_model=...)` | `gpt-image-1` |
| 로고 시안 개수 | `main.py`의 `LOGO_COUNT` | `2` |
| 이미지 크기 | `generate_logo_image(size=...)` | `1024x1024` |
