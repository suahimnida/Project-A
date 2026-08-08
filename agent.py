import os
import json
import base64
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


class BrandAgent:
    """OpenAI API를 사용해 브랜드 아이덴티티 요소를 생성하는 에이전트."""

    def __init__(
        self,
        api_key: str | None = None,
        text_model: str = "gpt-4o-mini",
        image_model: str = "gpt-image-1",
    ):
        # .env 파일의 환경변수를 불러온다.
        load_dotenv()

        # API 키는 직접 코드에 작성하지 않고
        # 생성자 인자 또는 환경변수에서 가져온다.
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY 환경변수가 설정되지 않았습니다.\n"
                ".env 파일에 다음과 같이 설정하세요:\n"
                "OPENAI_API_KEY=your_api_key\n\n"
                "또는 터미널에서 환경변수를 설정하세요."
            )

        self.text_model = text_model
        self.image_model = image_model
        self.client = OpenAI(api_key=self.api_key)

    @staticmethod
    def build_prompt(brief: dict[str, Any]) -> str:
        """브랜드 브리프를 바탕으로 LLM 프롬프트를 생성한다."""

        industry = brief["industry"]
        target = brief["target"]
        keywords = ", ".join(brief["keywords"])
        tone = brief.get("tone", "신뢰감 있고 대중적인")
        competitors = ", ".join(brief.get("competitors", [])) or "없음"
        notes = brief.get("notes", "특별한 요청사항 없음")

        return f"""
당신은 최고 수준의 브랜드 컨설팅 전문가입니다.
아래 브랜드 브리프를 분석하고 브랜드 아이덴티티 요소를 생성해 주세요.

[브랜드 브리프]
- 업종: {industry}
- 타겟: {target}
- 핵심 키워드: {keywords}
- 톤앤매너: {tone}
- 경쟁사: {competitors}
- 추가 요청사항: {notes}

[생성해야 할 결과]

1. namings
- 브랜드명 후보 3~5개
- 각 항목에는 다음 필드를 포함:
  - name: 한글 브랜드명
  - name_en: 영문 브랜드명
  - meaning: 브랜드명의 의미와 유래

2. slogans
- 브랜드의 톤앤매너를 반영한 슬로건 3개

3. story
- 약 300자 내외의 브랜드 스토리
- 탄생 배경
- 브랜드 철학
- 브랜드가 추구하는 비전
을 포함

4. color_palette
- main: 메인 컬러 HEX 코드 1개
- sub: 서브 컬러 HEX 코드 2~3개
- 반드시 #RRGGBB 형식의 6자리 HEX 코드 사용

5. logo_prompt
- 이미지 생성 모델에서 사용할 영문 로고 프롬프트
- 깔끔하고 직관적인 브랜드 로고
- 불필요하게 복잡한 디자인은 피할 것
- 벡터 로고 스타일을 지향할 것

6. differentiation
- 경쟁사가 존재하는 경우 경쟁사 대비 차별화 포인트 2~3개
- 경쟁사가 없는 경우 빈 배열 []

[중요]
반드시 아래 JSON 구조만 반환하세요.
Markdown 코드 블록이나 추가 설명을 포함하지 마세요.

{{
    "namings": [
        {{
            "name": "브랜드명",
            "name_en": "BrandName",
            "meaning": "브랜드명의 의미와 유래"
        }}
    ],
    "slogans": ["슬로건1", "슬로건2", "슬로건3"],
    "story": "브랜드 스토리 내용...",
    "color_palette": {{
        "main": "#RRGGBB",
        "sub": ["#RRGGBB", "#RRGGBB"]
    }},
    "logo_prompt": "A clean vector logo icon for...",
    "differentiation": ["차별화 포인트1", "차별화 포인트2"]
}}
"""

    @staticmethod
    def validate_result(result: dict[str, Any]) -> None:
        """LLM이 반환한 결과의 기본 구조를 검증한다."""

        required_fields = [
            "namings",
            "slogans",
            "story",
            "color_palette",
            "logo_prompt",
            "differentiation",
        ]

        for field in required_fields:
            if field not in result:
                raise ValueError(f"LLM 응답에 필수 필드가 없습니다: {field}")

        if not isinstance(result["namings"], list):
            raise ValueError("namings는 배열이어야 합니다.")

        if not isinstance(result["slogans"], list):
            raise ValueError("slogans는 배열이어야 합니다.")

        if not isinstance(result["story"], str):
            raise ValueError("story는 문자열이어야 합니다.")

        if not isinstance(result["color_palette"], dict):
            raise ValueError("color_palette는 객체여야 합니다.")

        if not isinstance(result["differentiation"], list):
            raise ValueError("differentiation은 배열이어야 합니다.")

        color_palette = result["color_palette"]

        if "main" not in color_palette:
            raise ValueError("color_palette.main이 없습니다.")

        if "sub" not in color_palette:
            raise ValueError("color_palette.sub가 없습니다.")

        if not isinstance(color_palette["sub"], list):
            raise ValueError("color_palette.sub는 배열이어야 합니다.")

    def generate_brand_elements(
        self,
        brief: dict[str, Any],
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """브리프를 받아 LLM을 호출하고 브랜드 요소를 반환한다."""

        prompt = self.build_prompt(brief)

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
        except Exception as e:
            raise RuntimeError(
                "LLM API 호출에 실패했습니다. "
                "API 키, API 사용 권한 및 잔액을 확인하세요."
            ) from e

        content = response.choices[0].message.content

        if not content:
            raise ValueError("LLM 응답 내용이 비어 있습니다.")

        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError("LLM 응답을 JSON으로 변환하지 못했습니다.") from e

        self.validate_result(result)

        return result

    def generate_logo_image(
        self,
        prompt: str,
        size: str = "1024x1024",
    ) -> bytes:
        """이미지 생성 API를 호출하여 PNG 바이트를 반환한다."""

        try:
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                n=1,
            )
        except Exception as e:
            raise RuntimeError(
                "이미지 생성 API 호출에 실패했습니다. "
                "API 키, API 사용 권한 및 잔액을 확인하세요."
            ) from e

        if not response.data:
            raise ValueError("이미지 생성 API 응답에 이미지 데이터가 없습니다.")

        image_base64 = response.data[0].b64_json

        if not image_base64:
            raise ValueError("이미지 생성 응답에 b64_json 데이터가 없습니다.")

        try:
            return base64.b64decode(image_base64)
        except Exception as e:
            raise ValueError("Base64 이미지 데이터를 디코딩하지 못했습니다.") from e
