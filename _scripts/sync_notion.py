import os
import sys
import re
import glob
import requests
from datetime import datetime
from notion_client import Client

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

def get_local_post_map():
    post_map = {}
    md_files = glob.glob(os.path.join(POSTS_DIR, "**/*.md"), recursive=True)
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"^notion_page_id:\s*([a-f0-9-]+)", content, re.MULTILINE)
                if match:
                    post_map[match.group(1)] = file_path
        except Exception as e:
            print(f"  - 로컬 파일 스캔 중 오류: {file_path} ({e})")
    return post_map

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"  - 이미지 다운로드 오류: {url} ({e})")
        return False

def rich_text_to_markdown(rich_text_list):
    md_parts = []
    for rt in rich_text_list:
        content = rt.get('plain_text', '')
        annotations = rt.get('annotations', {})
        if annotations.get('bold'): content = f"**{content}**"
        if annotations.get('italic'): content = f"*{content}*"
        if annotations.get('strikethrough'): content = f"~~{content}~~"
        if annotations.get('code'): content = f"`{content}`"
        
        link = rt.get('href')
        if link:
            md_parts.append(f"[{content}]({link})")
        else:
            md_parts.append(content)
    return "".join(md_parts)

def block_to_markdown(block):
    block_type = block['type']
    
    if block_type == 'paragraph':
        return rich_text_to_markdown(block['paragraph']['rich_text']) + "\n"
    elif block_type == 'heading_1':
        return f"# {rich_text_to_markdown(block['heading_1']['rich_text'])}\n"
    elif block_type == 'heading_2':
        return f"## {rich_text_to_markdown(block['heading_2']['rich_text'])}\n"
    elif block_type == 'heading_3':
        return f"### {rich_text_to_markdown(block['heading_3']['rich_text'])}\n"
    elif block_type == 'bulleted_list_item':
        return f"- {rich_text_to_markdown(block['bulleted_list_item']['rich_text'])}\n"
    elif block_type == 'numbered_list_item':
        return f"1. {rich_text_to_markdown(block['numbered_list_item']['rich_text'])}\n"
    elif block_type == 'to_do':
        checked = block['to_do']['checked']
        prefix = "- [x]" if checked else "- [ ]"
        return f"{prefix} {rich_text_to_markdown(block['to_do']['rich_text'])}\n"
    elif block_type == 'quote':
        return f"> {rich_text_to_markdown(block['quote']['rich_text'])}\n"
    elif block_type == 'divider':
        return "---\n"
    elif block_type == 'code':
        language = block['code']['language']
        code = rich_text_to_markdown(block['code']['rich_text'])
        return f"```{language}\n{code}\n```\n"
    elif block_type == 'image':
        img_block = block['image']
        img_type = img_block['type']
        
        if img_type == 'external':
            url = img_block['external']['url']
            return f"![image]({url})\n"
        elif img_type == 'file':
            url = img_block['file']['url']
            filename = os.path.basename(url.split('?')[0])
            save_path = os.path.join(IMG_DIR, filename)
            if download_image(url, save_path):
                return f"![image](/assets/img/{filename})\n"
            else:
                return "<!-- 이미지 다운로드 실패 -->\n"
    return ""

def page_to_markdown(notion_client, page_id):
    markdown_content = []
    
    paginated_blocks = notion_client.blocks.children.list(block_id=page_id)
    blocks = paginated_blocks.get('results', [])
    
    for block in blocks:
        markdown_content.append(block_to_markdown(block))
        
    return "\n".join(markdown_content)

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

        if current_status == STATUS_DELETED_VALUE:
            if page_id in local_post_map:
                file_to_delete = local_post_map[page_id]
                os.remove(file_to_delete)
                print(f"삭제 완료: {file_to_delete}")
            else:
                print(f"삭제 건너뜀: 로컬에서 해당 포스트를 찾을 수 없습니다 (ID: {page_id})")
            
            try:
                notion.pages.update(page_id=page_id, properties={STATUS_PROPERTY_NAME: {"status": {"name": STATUS_ARCHIVED_VALUE}}})
                print(f"  - Notion 상태를 '{STATUS_ARCHIVED_VALUE}'로 변경했습니다.")
            except Exception as e:
                print(f"  - Notion 상태 변경 중 오류: {e}")
            continue

        if current_status == STATUS_PUBLISH_VALUE:
            if page_id in local_post_map:
                os.remove(local_post_map[page_id])
                print(f"기존 파일 삭제: {local_post_map[page_id]} (업데이트를 위해)")

            title = rich_text_to_markdown(properties[TITLE_PROPERTY_NAME]["title"])
            slug_prop = properties.get(SLUG_PROPERTY_NAME, {})
            slug = rich_text_to_markdown(slug_prop.get("rich_text", [])) if slug_prop.get("rich_text") else slugify(title)
            
            last_modified_at = datetime.fromisoformat(page["last_edited_time"]).isoformat()
            created_date = datetime.fromisoformat(page["created_time"]).strftime("%Y-%m-%d")
            
            category_prop = properties.get(CATEGORY_PROPERTY_NAME, {})
            category = (category_prop.get("select") or {}).get("name", "Uncategorized")
            
            tags_prop = properties.get(TAGS_PROPERTY_NAME, {})
            tags = [tag["name"] for tag in tags_prop.get("multi_select", [])]

            print(f"처리 중: '{title}'")

            front_matter_list = [
                "---",
                f'title: "{title}"',
                f'last_modified_at: {last_modified_at}',
                f'notion_page_id: {page_id}',
                'layout: post',
                'categories:',
                f'    - {category}',
                'excerpt: ""',
                'toc: true',
                'toc_sticky: true',
                'toc_icon: "cog"',
                'author_profile: true',
                'mathjax: true',
                f'tag: [{", ".join(tags)}]',
                "---"
            ]
            front_matter = "\n".join(front_matter_list)

            try:
                markdown_content = page_to_markdown(notion, page_id)
            except Exception as e:
                print(f"  - '{title}' 콘텐츠 변환 중 오류: {e}")
                continue

            category_dir = os.path.join(POSTS_DIR, category)
            os.makedirs(category_dir, exist_ok=True)
            file_name = f"{created_date}-{slug}.md"
            file_path = os.path.join(category_dir, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                # 머리말과 본문 사이에 명시적으로 2개의 줄바꿈을 추가하고,
                # 본문 시작 부분의 모든 공백/줄바꿈을 제거하여 안정성 확보
                f.write(front_matter + "\n\n" + markdown_content.lstrip())
            print(f"  - 저장 완료: {file_path}")

            try:
                notion.pages.update(page_id=page_id, properties={STATUS_PROPERTY_NAME: {"status": {"name": STATUS_ARCHIVED_VALUE}}})
                print(f"  - Notion 상태를 '{STATUS_ARCHIVED_VALUE}'로 변경했습니다.")
            except Exception as e:
                print(f"  - Notion 상태 변경 중 오류: {e}")

    for dirpath, _, filenames in os.walk(POSTS_DIR, topdown=False):
        if not filenames and not os.listdir(dirpath):
            if dirpath != POSTS_DIR:
                os.rmdir(dirpath)
                print(f"빈 폴더 삭제: {dirpath}")

    print("\n모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
