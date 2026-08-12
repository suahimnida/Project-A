import json
import os
import re
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from agent import BrandAgent

# 생성할 로고 시안 개수 (요구사항: 2~3개)
LOGO_COUNT = 2

def load_brief(brief_path: str) -> dict[str, Any] | None:
    """
        브랜드 브리프 JSON 파일을 읽고 필수 필드를 검증한다.
        실패하면 None을 반환한다.
    """

    try:
        with open(brief_path, "r", encoding="utf-8") as f:
            brief = json.load(f)
    except FileNotFoundError:
        print(f"❌ [오류] 파일을 찾을 수 없습니다: {brief_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ [오류] JSON 형식이 올바르지 않습니다: {e}")
        return None
    except OSError as e:
        print(f"❌ [오류] JSON 파일을 읽을 수 없습니다: {e}")
        return None

    if not isinstance(brief, dict):
        print("❌ [오류] 브리프 JSON의 최상위 구조는 객체여야 합니다.")
        return None

    # 필수 필드 존재 검증
    required_fields = ["industry", "target", "keywords"]

    for field in required_fields:
        if field not in brief:
            print(f"❌ [오류] 필수 입력 필드가 누락되었습니다: {field}")
            return None

    # industry 검증
    if not isinstance(brief["industry"], str) or not brief["industry"].strip():
        print("❌ [오류] industry는 비어 있지 않은 문자열이어야 합니다.")
        return None

    # target 검증
    if not isinstance(brief["target"], str) or not brief["target"].strip():
        print("❌ [오류] target은 비어 있지 않은 문자열이어야 합니다.")
        return None

    # keywords 검증
    if not isinstance(brief["keywords"], list) or not brief["keywords"]:
        print("❌ [오류] keywords는 하나 이상의 키워드를 포함해야 합니다.")
        return None

    if not all(
        isinstance(keyword, str) and keyword.strip()
        for keyword in brief["keywords"]
    ):
        print("❌ [오류] keywords의 모든 값은 비어 있지 않은 문자열이어야 합니다.")
        return None

    return brief


def is_valid_hex(value: str) -> bool:
    # 6자리 HEX 컬러 코드인지 확인한다.

    return bool(isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value))

def save_color_palette(color_data: dict[str, Any], output_dir: str) -> None:
    # 컬러 팔레트를 matplotlib으로 시각화하여 PNG로 저장한다.

    main_hex = color_data.get("main")
    sub_hexes = color_data.get("sub", [])

    if not is_valid_hex(main_hex):
        raise ValueError(f"잘못된 메인 컬러 HEX 코드입니다: {main_hex}")

    if not isinstance(sub_hexes, list):
        raise ValueError("서브 컬러 데이터가 배열이 아닙니다.")

    for hex_code in sub_hexes:
        if not is_valid_hex(hex_code):
            raise ValueError(f"잘못된 서브 컬러 HEX 코드입니다: {hex_code}")

    colors = [main_hex] + sub_hexes
    labels = ["Main"] + [f"Sub {i + 1}" for i in range(len(sub_hexes))]

    fig, ax = plt.subplots(figsize=(len(colors) * 2.5, 2))
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.axis("off")

    for i, (hex_code, label) in enumerate(zip(colors, labels)):
        rect = patches.Rectangle((i, 0), 1, 1, facecolor=hex_code)
        ax.add_patch(rect)
        ax.text(
            i + 0.5,
            0.5,
            f"{label}\n{hex_code}",
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.3),
        )

    color_path = os.path.join(output_dir, "color_palette.png")

    plt.tight_layout()
    plt.savefig(color_path, bbox_inches="tight", dpi=300)
    plt.close(fig)

    print(f"  - 저장: {color_path}")

def create_logo_variation_prompt(base_prompt: str, variation_number: int) -> str:
    """
        동일한 브랜드 아이덴티티를 유지하면서 서로 다른 로고 시안을
        생성하기 위한 프롬프트를 만든다.
    """

    variations = {
        1: (
            "Create a primary logo concept emphasizing "
            "a simple and memorable symbol."
        ),
        2: (
            "Create an alternative logo concept emphasizing "
            "a refined wordmark and distinctive typography."
        ),
        3: (
            "Create a third alternative logo concept emphasizing "
            "a minimal geometric symbol and modern composition."
        ),
    }

    variation = variations.get(variation_number, "Create a distinct alternative logo concept.")

    return f"""
{base_prompt}

{variation}

Keep the overall brand identity, tone, and visual direction consistent.
Make this concept visually distinct from other variations.
Use a clean, professional, minimal vector-logo aesthetic.
Avoid mockups, photographs, 3D renders, and unnecessary decorative elements.
"""

def print_brand_result(ai_result: dict[str, Any]) -> None:
    # 생성된 브랜드 결과를 CLI에 출력한다.

    print("\n  [네이밍]")

    for item in ai_result.get("namings", []):
        name = item.get("name", "")
        name_en = item.get("name_en", "")
        meaning = item.get("meaning", "")

        title = f"{name} ({name_en})" if name_en else name
        print(f"    - {title}: {meaning}")

    print("\n  [슬로건]")

    for slogan in ai_result.get("slogans", []):
        print(f'    - "{slogan}"')

    story = ai_result.get("story", "")
    print(f"\n  [스토리] 생성 완료 ({len(story)}자)")
    print(f"\n{story}")

    differentiation = ai_result.get("differentiation", [])

    if differentiation:
        print("\n  [차별화 포인트]")

        for point in differentiation:
            print(f"    - {point}")


def run_brand_generator() -> None:
    # 브랜드 아이덴티티 생성 전체 workflow를 실행한다.

    print("\n🎨 AI 브랜드 아이덴티티 생성기")
    print("=" * 50)

    # ------------------------------------------------
    # Step 0. 에이전트 초기화
    # ------------------------------------------------
    try:
        agent = BrandAgent()
    except ValueError as e:
        print(f"❌ [오류] {e}")
        return

    # ------------------------------------------------
    # Step 1. 사용자 입력
    # ------------------------------------------------
    brief_path = input("브리프 파일 경로를 입력하세요: ").strip()

    if not brief_path:
        print("❌ [오류] 브리프 파일 경로를 입력해야 합니다.")
        return

    if not os.path.isfile(brief_path):
        print(f"❌ [오류] 파일이 존재하지 않습니다: {brief_path}")
        return

    output_dir = input("출력 폴더 경로를 입력하세요 (엔터 시 ./output): ").strip()

    if not output_dir:
        output_dir = "./output"

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"❌ [오류] 출력 폴더를 생성할 수 없습니다: {e}")
        return

    # ------------------------------------------------
    # Step 2. 브랜드 브리프 읽기
    # ------------------------------------------------
    brief = load_brief(brief_path)

    if brief is None:
        return

    print("\n[1/5] 브랜드 요소 생성 중...")

    # ------------------------------------------------
    # Step 3. LLM 텍스트 요소 생성
    # ------------------------------------------------
    ai_result: dict[str, Any] = {
        "namings": [],
        "slogans": [],
        "story": "",
        "color_palette": {},
        "logo_prompt": "",
        "differentiation": [],
    }

    try:
        ai_result = agent.generate_brand_elements(brief)
        print_brand_result(ai_result)
    except Exception as e:
        # LLM이 실패하더라도 프로그램 전체를 종료하지 않는다.
        print(f"❌ LLM API 호출 실패: {e}")
        print("  ⚠️ 텍스트 기반 브랜드 요소 생성을 건너뛰고 다음 단계로 진행합니다.")

    # ------------------------------------------------
    # Step 4. 컬러 팔레트 생성 및 저장
    # ------------------------------------------------
    print("\n[2/5] 컬러 팔레트 시각화 중...")

    color_data = ai_result.get("color_palette", {})

    if not color_data:
        print("  ⚠️ 컬러 팔레트 데이터가 없어 시각화를 건너뜁니다.")
    else:
        main_color = color_data.get("main", "(없음)")
        sub_colors = color_data.get("sub", [])

        print(f"  - 메인: {main_color}")
        print(f"  - 서브: {', '.join(sub_colors) or '(없음)'}")

        try:
            save_color_palette(color_data, output_dir)
        except Exception as e:
            print(f"  ⚠️ 컬러 팔레트 생성 실패 (다음 단계 진행): {e}")

    # ------------------------------------------------
    # Step 5. 로고 시안 생성
    # ------------------------------------------------
    print(f"\n[3/5] 로고 시안 {LOGO_COUNT}개 생성 중...")

    logo_prompt = ai_result.get("logo_prompt")

    if not logo_prompt:
        print("  ⚠️ logo_prompt가 없어 로고 생성을 건너뜁니다.")
    else:
        for i in range(1, LOGO_COUNT + 1):
            try:
                variation_prompt = create_logo_variation_prompt(logo_prompt, i)
                image_bytes = agent.generate_logo_image(variation_prompt)

                logo_path = os.path.join(output_dir, f"logo_0{i}.png")

                with open(logo_path, "wb") as f:
                    f.write(image_bytes)

                print(f"  - 저장: {logo_path}")
            except Exception as e:
                # 하나의 로고 생성에 실패해도 다음 로고 생성을 계속한다.
                print(f"  ⚠️ 로고 시안 0{i} 생성 실패 (다음 진행): {e}")

    # ------------------------------------------------
    # Step 6. 전체 결과 JSON 저장
    # ------------------------------------------------
    print("\n[4/5] 전체 결과 JSON 저장 중...")

    result_data = {"brief": brief, "result": ai_result}

    try:
        json_save_path = os.path.join(output_dir, "brand_result.json")

        with open(json_save_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"  - 저장: {json_save_path}")
    except OSError as e:
        print(f"❌ JSON 결과 저장 실패: {e}")

    # ------------------------------------------------
    # Step 7. 완료
    # ------------------------------------------------
    print("\n[5/5] 작업 완료!")
    print(f"✅ 완료! {os.path.abspath(output_dir)} 폴더를 확인하세요.\n")


if __name__ == "__main__":
    run_brand_generator()
