import os
import sys
import re
import glob
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
STATUS_PUBLISH_VALUE = "published"
STATUS_DELETED_VALUE = "deleted"
STATUS_ARCHIVED_VALUE = "archived"

# --- 환경 변수 로드 ---
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")
POSTS_DIR = "_posts"
IMG_DIR = "assets/img"

def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9\u3131-\u3163\uac00-\ud7a3\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    text = text.strip("-")
    return text.lower()

def replace_image_path(match):
    """re.sub를 위한 헬퍼 함수. 로컬 이미지 경로만 수정합니다."""
    alt_text = match.group(1)
    url = match.group(2)
    if url.startswith("http"):
        return match.group(0)  # http/https로 시작하는 외부 링크는 그대로 반환
    return f"![{alt_text}](/assets/img/{url})"

def get_local_post_map():
    """_posts 폴더를 스캔하여 notion_page_id와 파일 경로의 맵을 생성"""
    post_map = {}
    md_files = glob.glob(os.path.join(POSTS_DIR, "**/*.md"), recursive=True)
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"^notion_page_id:\s*([a-f0-9-]+)", content, re.MULTILINE)
                if match:
                    page_id = match.group(1)
                    post_map[page_id] = file_path
        except Exception as e:
            print(f"  - 로컬 파일 스캔 중 오류: {file_path} ({e})")
    return post_map

def main():
    if not NOTION_API_KEY or not DATABASE_ID:
        print("오류: NOTION_API_KEY와 DATABASE_ID 환경 변수를 설정해야 합니다.")
        sys.exit(1)

    notion = Client(auth=NOTION_API_KEY)
    local_post_map = get_local_post_map()
    print(f"로컬에서 {len(local_post_map)}개의 기존 포스트를 찾았습니다.")

    print(f"'{STATUS_PUBLISH_VALUE}' 또는 '{STATUS_DELETED_VALUE}' 상태인 포스트를 Notion에서 검색합니다...")
    try:
        query_results = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "or": [
                    {"property": STATUS_PROPERTY_NAME, "status": {"equals": STATUS_PUBLISH_VALUE}},
                    {"property": STATUS_PROPERTY_NAME, "status": {"equals": STATUS_DELETED_VALUE}},
                ]
            },
            sorts=[{"timestamp": "created_time", "direction": "descending"}]
        ).get("results")
    except Exception as e:
        print(f"Notion API 쿼리 중 오류 발생: {e}")
        sys.exit(1)

    if not query_results:
        print("동기화할 포스트가 없습니다.")
        return

    print(f"{len(query_results)}개의 동기화할 포스트를 찾았습니다.")
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    for page in query_results:
        page_id = page["id"]
        properties = page["properties"]
        current_status = properties[STATUS_PROPERTY_NAME]["status"]["name"]

        # --- 삭제 처리 ---
        if current_status == STATUS_DELETED_VALUE:
            if page_id in local_post_map:
                file_to_delete = local_post_map[page_id]
                os.remove(file_to_delete)
                print(f"삭제 완료: {file_to_delete}")
            else:
                print(f"삭제 건너뜀: 로컬에서 해당 포스트를 찾을 수 없습니다 (ID: {page_id})")
            
            # Notion 상태를 'archived'로 변경
            try:
                notion.pages.update(
                    page_id=page_id,
                    properties={STATUS_PROPERTY_NAME: {"status": {"name": STATUS_ARCHIVED_VALUE}}}
                )
                print(f"  - Notion 상태를 '{STATUS_ARCHIVED_VALUE}'로 변경했습니다.")
            except Exception as e:
                print(f"  - Notion 상태 변경 중 오류: {e}")
            continue

        # --- 생성/수정 처리 ---
        if current_status == STATUS_PUBLISH_VALUE:
            # 기존 파일이 있으면 삭제 (수정 시 경로가 바뀔 수 있으므로)
            if page_id in local_post_map:
                os.remove(local_post_map[page_id])
                print(f"기존 파일 삭제: {local_post_map[page_id]} (업데이트를 위해)")

            title = properties[TITLE_PROPERTY_NAME]["title"][0]["plain_text"]
            slug_prop = properties.get(SLUG_PROPERTY_NAME, {})
            slug = slug_prop["rich_text"][0]["plain_text"] if slug_prop and slug_prop.get("rich_text") else slugify(title)
            
            last_modified_at = datetime.fromisoformat(page["last_edited_time"]).isoformat()
            created_date = datetime.fromisoformat(page["created_time"]).strftime("%Y-%m-%d")
            
            category_prop = properties.get(CATEGORY_PROPERTY_NAME, {})
            category = (category_prop.get("select") or {}).get("name", "Uncategorized")
            
            tags_prop = properties.get(TAGS_PROPERTY_NAME, {})
            tags = [tag["name"] for tag in tags_prop.get("multi_select", [])]

            print(f"처리 중: '{title}'")

            front_matter = f"""
---
title: "{title}"
last_modified_at: {last_modified_at}
notion_page_id: {page_id}
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
            try:
                exporter = StringExporter(block_id=page_id, output_path=IMG_DIR, token=NOTION_API_KEY)
                markdown_content = exporter.export()
                markdown_content = re.sub(r"!\(.*?)\)", replace_image_path, markdown_content)
            except Exception as e:
                print(f"  - '{title}' 콘텐츠 변환 중 오류: {e}")
                continue

            category_dir = os.path.join(POSTS_DIR, category)
            os.makedirs(category_dir, exist_ok=True)
            file_name = f"{created_date}-{slug}.md"
            file_path = os.path.join(category_dir, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(front_matter + markdown_content)
            print(f"  - 저장 완료: {file_path}")

            try:
                notion.pages.update(
                    page_id=page_id,
                    properties={STATUS_PROPERTY_NAME: {"status": {"name": STATUS_ARCHIVED_VALUE}}}
                )
                print(f"  - Notion 상태를 '{STATUS_ARCHIVED_VALUE}'로 변경했습니다.")
            except Exception as e:
                print(f"  - Notion 상태 변경 중 오류: {e}")

    # --- 빈 카테고리 폴더 정리 ---
    for dirpath, _, filenames in os.walk(POSTS_DIR, topdown=False):
        if not filenames and not os.listdir(dirpath): # 파일도 없고 하위 폴더도 없으면
            if dirpath != POSTS_DIR: # _posts 최상위는 삭제하지 않음
                os.rmdir(dirpath)
                print(f"빈 폴더 삭제: {dirpath}")

    print("\n모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
