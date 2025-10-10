import os
import sys
import re
from datetime import datetime
from notion_client import Client
from notion2md.exporter.block import StringExporter

# --- Notion 데이터베이스 속성 이름 설정 ---
STATUS_PROPERTY_NAME = "status"
TITLE_PROPERTY_NAME = "title"
TAGS_PROPERTY_NAME = "tags"
CATEGORY_PROPERTY_NAME = "category"
SLUG_PROPERTY_NAME = "slug"

# --- 처리할 상태 값 설정 ---
# 이 상태 값을 가진 페이지만 블로그 포스트로 생성합니다.
STATUS_PUBLISH_VALUE = "published"
# 처리가 완료된 후 변경될 상태 값
STATUS_ARCHIVED_VALUE = "archived"

# --- 환경 변수 로드 ---
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")
POSTS_DIR = "_posts"
IMG_DIR = "assets/img"

# --- Slug 변환 함수 ---
def slugify(text):
    # 한글을 제외한 모든 비-알파벳/숫자 문자를 제거
    text = re.sub(r"[^a-zA-Z0-9\u3131-\u3163\uac00-\ud7a3\s-]", "", text)
    # 공백이나 연속된 하이픈을 단일 하이픈으로 변환
    text = re.sub(r"[\s-]+", "-", text)
    # 앞뒤 하이픈 제거
    text = text.strip("-")
    return text.lower()

def main():
    if not NOTION_API_KEY or not DATABASE_ID:
        print("오류: NOTION_API_KEY와 DATABASE_ID 환경 변수를 설정해야 합니다.")
        sys.exit(1)

    notion = Client(auth=NOTION_API_KEY)
    print(f"'{STATUS_PUBLISH_VALUE}' 상태인 포스트를 Notion에서 검색합니다...")

    # Notion 데이터베이스 쿼리
    try:
        query_results = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": STATUS_PROPERTY_NAME,
                "select": {"equals": STATUS_PUBLISH_VALUE},
            },
            sorts=[{"timestamp": "created_time", "direction": "descending"}]
        ).get("results")
    except Exception as e:
        print(f"Notion API 쿼리 중 오류 발생: {e}")
        sys.exit(1)

    if not query_results:
        print("새로 발행할 포스트가 없습니다.")
        return

    print(f"{len(query_results)}개의 새 포스트를 찾았습니다.")
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    for page in query_results:
        page_id = page["id"]
        properties = page["properties"]

        # --- Front Matter 정보 추출 ---
        title = properties[TITLE_PROPERTY_NAME]["title"][0]["plain_text"]
        
        # Slug 처리: Slug 속성이 있으면 사용, 없으면 제목으로 생성
        slug_prop = properties.get(SLUG_PROPERTY_NAME, {})
        if slug_prop and slug_prop.get("rich_text"):
            slug = slug_prop["rich_text"][0]["plain_text"]
        else:
            slug = slugify(title)

        last_modified_at = datetime.fromisoformat(page["last_edited_time"]).isoformat()
        created_date = datetime.fromisoformat(page["created_time"]).strftime("%Y-%m-%d")
        
        category_prop = properties.get(CATEGORY_PROPERTY_NAME, {})
        category = category_prop.get("select", {}).get("name", "Uncategorized")

        tags_prop = properties.get(TAGS_PROPERTY_NAME, {})
        tags = [tag["name"] for tag in tags_prop.get("multi_select", [])]

        print(f"처리 중: '{title}'")

        # --- Jekyll Front Matter 생성 (기존 포스트 형식에 맞춤) ---
        front_matter = f"""---
title: "{title}"
last_modified_at: {last_modified_at}
layout: post
categories:
    - {category}
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [{', '.join(tags)}]
---

"""
        # --- Notion 페이지 콘텐츠를 Markdown으로 변환 ---
        try:
            # StringExporter를 사용하여 페이지 콘텐츠를 Markdown 문자열로 변환
            # 이미지 등 첨부파일은 IMG_DIR에 저장
            exporter = StringExporter(block_id=page_id, output_path=IMG_DIR, token=NOTION_API_KEY)
            markdown_content = exporter.export()

            # notion2md가 생성하는 상대 이미지 경로를 Jekyll 형식에 맞게 절대 경로로 변환
            # 예: ![...](image.png) -> ![...](/assets/img/image.png)
            # 외부 URL(http, https)은 변경하지 않음
            markdown_content = re.sub(r"!\[(.*?)\]\((?!https?://)(.*?)\)", r"![\1](/assets/img/\2)", markdown_content)
        except Exception as e:
            print(f"  - '{title}' 콘텐츠 변환 중 오류: {e}")
            continue

        # --- 파일 저장 ---
        file_name = f"{created_date}-{slug}.md"
        file_path = os.path.join(POSTS_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(front_matter + markdown_content)
        
        print(f"  - 저장 완료: {file_path}")

        try:
            notion.pages.update(
                page_id=page_id,
                properties={
                    STATUS_PROPERTY_NAME: {"select": {"name": STATUS_ARCHIVED_VALUE}}
                }
            )
            print(f"  - Notion 상태를 '{STATUS_ARCHIVED_VALUE}'로 변경했습니다.")
        except Exception as e:
            print(f"  - Notion 상태 변경 중 오류: {e}")

    print("\n모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
