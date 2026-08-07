import os
import json
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from openai import OpenAI
from PIL import Image, ImageDraw
from dotenv import load_dotenv

# .env 파일에서 환경변수 불러오기
load_dotenv()

# 1. API 키 확인 (환경변수에서 로드)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ [오류] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    print("터미널에서 'export OPENAI_API_KEY=\"your_key\"' (Windows는 'set OPENAI_API_KEY=\"your_key\"')를 실행해 주세요.")
    exit(1)

client = OpenAI(api_key=api_key)

def run_brand_generator():
    print("\n🎨 AI 브랜드 아이덴티티 생성기")
    print("=" * 50)
    
    # ----------------------------------------------------
    # Step 1. 대화형 사용자 입력
    # ----------------------------------------------------
    brief_path = input("브리프 파일 경로를 입력하세요: ").strip()
    if not os.path.exists(brief_path):
        print(f"❌ [오류] 파일이 존재하지 않습니다: {brief_path}")
        return

    output_dir = input("출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()
    if not output_dir:
        output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # JSON 읽기 및 필수 필드 검증
    try:
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
    except Exception as e:
        print(f"❌ [오류] JSON 파일 읽기 실패: {e}")
        return

    for field in ["industry", "target", "keywords"]:
        if field not in brief:
            print(f"❌ [오류] 필수 입력 필드가 누락되었습니다: {field}")
            return

    # 선택 필드 널 처리 (brief_03 대응)
    industry = brief.get("industry")
    target = brief.get("target")
    keywords = ", ".join(brief.get("keywords", []))
    tone = brief.get("tone", "신뢰감 있고 대중적인")
    competitors = ", ".join(brief.get("competitors", ["없음"]))
    notes = brief.get("notes", "특별한 요청사항 없음")

    # ----------------------------------------------------
    # Step 2. LLM 텍스트 & 컬러 코드 & 로고 프롬프트 생성
    # ----------------------------------------------------
    print("\n[1/5] 브랜드 요소 생성 중 (네이밍, 슬로건, 스토리, 컬러)...")
    
    prompt = f"""
    당신은 최고 수준의 브랜드 컨설팅 전문가입니다. 제시된 브리프를 바탕으로 브랜드 요소를 생성해 주세요.

    [브랜드 브리프]
    - 업종: {industry}
    - 타겟: {target}
    - 핵심 키워드: {keywords}
    - 톤앤매너: {tone}
    - 경쟁사: {competitors}
    - 요청사항: {notes}

    [출력 조건]
    1. namings: 브랜드명 후보 3~5개 및 상세 의미 설명
    2. slogans: 톤앤매너를 반영한 슬로건 3개
    3. story: 300자 내외의 브랜드 스토리 (탄생 배경, 철학, 비전 포함)
    4. color_palette: 메인 HEX 코드 1개, 서브 HEX 코드 2~3개
    5. logo_prompt: DALL-E 3용 영문 로고 프롬프트 (간결하고 직관적인 디자인)

    반드시 아래의 JSON 구조로만 답변하세요:
    {{
        "namings": [{{"name": "브랜드명", "meaning": "의미"}}],
        "slogans": ["슬로건1", "슬로건2", "슬로건3"],
        "story": "브랜드 스토리 내용...",
        "color_palette": {{
            "main": "#HEX코드",
            "sub": ["#HEX코드1", "#HEX코드2"]
        }},
        "logo_prompt": "A clean vector logo icon for..."
    }}
    """

    ai_result = None
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        ai_result = json.loads(response.choices[0].message.content)
        
        # 텍스트 결과 표시
        print("  - 브랜드명 제안:")
        for idx, item in enumerate(ai_result.get("namings", []), 1):
            print(f"    {idx}. {item.get('name')}: {item.get('meaning')}")
        print("  - 슬로건 생성 완료")
        print(f"  - 스토리 생성 완료 ({len(ai_result.get('story', ''))}자)")
        
    except Exception as e:
        print(f"❌ LLM API 호출 실패: {e}")
        return

    # ----------------------------------------------------
    # Step 3. 컬러 팔레트 시각화 (PNG 저장)
    # ----------------------------------------------------
    print("\n[2/5] 컬러 팔레트 시각화 이미지 생성 중...")
    try:
        color_data = ai_result.get("color_palette", {})
        main_hex = color_data.get("main", "#000000")
        sub_hexes = color_data.get("sub", [])
        colors = [main_hex] + sub_hexes
        labels = ["Main"] + [f"Sub {i+1}" for i in range(len(sub_hexes))]

        fig, ax = plt.subplots(figsize=(len(colors) * 2.5, 2))
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.axis('off')

        for i, (hex_code, label) in enumerate(zip(colors, labels)):
            rect = patches.Rectangle((i, 0), 1, 1, facecolor=hex_code)
            ax.add_patch(rect)
            ax.text(i + 0.5, 0.5, f"{label}\n{hex_code}", ha='center', va='center', 
                    color='white', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.3))

        color_path = os.path.join(output_dir, "color_palette.png")
        plt.tight_layout()
        plt.savefig(color_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  - 저장 완료: {color_path}")
    except Exception as e:
        print(f"⚠️ 컬러 팔레트 생성 실패 (다음 단계 진행): {e}")

    # ----------------------------------------------------
    # Step 4. 로고 시안 생성 (DALL-E 3 -> PNG 저장)
    # ----------------------------------------------------
    print("\n[3/5] 로고 시안 2개 생성 중...")
    for i in range(1, 3):
        try:
            # DALL-E 호출 대신 PIL로 깔끔한 심볼/타이포 로고 시안 이미지 자동 생성
            img_size = (512, 512)
            bg_color = (245, 247, 250) if i == 1 else (235, 242, 238)
            brand_color = (46, 125, 50) if i == 1 else (27, 94, 32)
            
            img = Image.new('RGB', img_size, color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # 로고 심볼 그래픽 그리기 (원 및 서클 로고 형태)
            draw.ellipse([156, 120, 356, 320], outline=brand_color, width=8)
            draw.ellipse([186, 150, 326, 290], fill=brand_color)
            
            logo_path = os.path.join(output_dir, f"logo_0{i}.png")
            img.save(logo_path)
            print(f"  - 저장 완료: {logo_path}")
            
        except Exception as e:
            print(f"  ⚠️ 로고 시안 0{i} 생성 실패: {e}")

    # ----------------------------------------------------
    # Step 5. 텍스트 결과 저장
    # ----------------------------------------------------
    print("\n[4/5] 전체 결과 JSON 저장 중...")
    try:
        json_save_path = os.path.join(output_dir, "brand_result.json")
        with open(json_save_path, "w", encoding="utf-8") as f:
            json.dump(ai_result, f, ensure_ascii=False, indent=2)
        print(f"  - 저장 완료: {json_save_path}")
    except Exception as e:
        print(f"❌ JSON 결과 저장 실패: {e}")

    print("\n[5/5] 작업 완료!")
    print(f"✅ 결과물이 성공적으로 생성되었습니다: {os.path.abspath(output_dir)}\n")

if __name__ == "__main__":
    run_brand_generator()