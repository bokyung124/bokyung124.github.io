---
title: "Notion과 GitHub Pages 블로그 연동하여 글쓰기 자동화하기"
last_modified_at: 2025-10-17T01:16:00+00:00
notion_page_id: 28e12b31-a8a8-8042-929a-f8c732b579f6
layout: post
categories:
  - CS
tags:
  - "Notion"
  - "Github Blog"
  - "Github Action"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

매번 VS Code로 글을 작성하기 번거로워서 노션 데이터베이스와 Github Blog (Jekyll) 을 연동하는 워크플로우를 생성했습니다. 
Github Actions를 통해 스크립트를 실행하고, 스케줄링합니다.

## **Notion과 GitHub Blog 연동의 장점**

- **효율적인 콘텐츠 작성**: Notion은 마크다운을 비롯한 다양한 블록을 지원하며, 이미지나 코드 조각을 삽입하기 매우 편리합니다.

- **체계적인 관리**: Notion의 데이터베이스 기능을 사용하여 글의 상태(작성 완료, 발행 완료, 삭제)를 체계적으로 관리할 수 있습니다.

- **자동화된 배포 파이프라인**: 글을 '발행' 상태로 변경하기만 하면, GitHub Actions가 자동으로 글을 발행하고 블로그를 배포합니다.

- **버전 관리 및 백업**: 모든 콘텐츠는 GitHub 리포지토리에 마크다운 파일로 저장되므로, 버전 관리가 용이합니다.

## **아키텍처**

자동화 파이프라인은 다음과 같은 흐름으로 동작합니다.

1. **Notion에서 글 작성**: Notion 데이터베이스에 새로운 글을 작성하고, 상태를 `Published`로 변경합니다.

2. **GitHub Actions 실행**: 설정된 스케줄(10분마다) 또는 main 브랜치에 코드 푸시 시 GitHub Actions 워크플로우가 실행됩니다.

3. **콘텐츠 동기화**: 워크플로우의 첫 번째 job이 Python 스크립트를 실행하여 Notion API를 통해 `Published` 또는 `Deleted` 상태의 글을 가져옵니다.

4. **파일 변환 및 commit**: 스크립트는 가져온 Notion 페이지를 마크다운 파일로 변환하고, 이미지를 다운로드하여 assets 폴더에 저장합니다. 변경 사항이 있으면 자동으로 커밋 및 푸시합니다.

5. **블로그 빌드 및 배포**: 위 과정을 통해 새로운 커밋이 감지되면, 워크플로우의 두 번째 job이 실행되어 사이트를 빌드하고 GitHub Pages에 배포합니다.

## 1단계: Notion 설정

### 1. Notion Integration 생성 및 API 키 발급

![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-10-16_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_7.21.14.png)

- [Notion 개발자 페이지](https://www.notion.so/my-integrations)로 이동하여 '새 API 통합'을 생성합니다.

- 필요한 권한을 선택합니다.
  - 콘텐츠 읽기
  - 콘텐츠 업데이트
  - 콘텐츠 입력

- 생성된 Integration의 '구성' 탭에서 **프라이빗 API 통합 시크릿 값** 을 복사합니다. 이 값이 `NOTION_API_KEY`가 됩니다.

### 2. 콘텐츠 데이터베이스 생성 및 연동

![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-10-16_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_7.22.15.png)

- 블로그 글을 관리할 Notion 데이터베이스를 생성합니다.

- 데이터베이스 우측 상단의 '...' 아이콘을 클릭하고 '연결'에서 방금 생성한 Integration을 검색하여 연결해줍니다.

- 브라우저에서 데이터베이스 URL을 확인합니다. `https://www.notion.so/{workspace_name}/{DATABASE_ID}?v=...` 형태에서 `DATABASE_ID` 부분을 복사합니다.

### 3. 데이터베이스 속성 설정

동기화 스크립트가 올바르게 동작하려면 데이터베이스의 속성을 다음과 같이 설정해야 합니다.

## 2단계: 동기화 스크립트 작성

Notion의 콘텐츠를 마크다운으로 변환하고, 이미지를 다운로드하는 Python 스크립트를 작성합니다.

- **경로**: `_scripts/sync_notion.py`

<details markdown="1">
  <summary>python 파일 예시</summary>

  ```python
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
      text = re.sub(r"[^a-zA-Z0-9\u3131-\u3163\uac00-\ud7a3\s-ről", "", text)
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
              for chunk in response.iter_content(chunk_size=812):
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
  
  def blocks_to_markdown(notion_client, blocks, indent_level=0):
      md_parts = []
      indent_space = "  " * indent_level
      numbered_list_start_index = 1
  
      for i, block in enumerate(blocks):
          block_type = block['type']
  
          is_numbered = block_type == 'numbered_list_item'
          if not is_numbered or (i > 0 and blocks[i-1]['type'] != 'numbered_list_item'):
              numbered_list_start_index = 1
  
          content = ""
          if block_type == 'paragraph':
              content = indent_space + rich_text_to_markdown(block['paragraph']['rich_text'])
          elif block_type == 'heading_1':
              content = f"# {rich_text_to_markdown(block['heading_1']['rich_text'])}"
          elif block_type == 'heading_2':
              content = f"## {rich_text_to_markdown(block['heading_2']['rich_text'])}"
          elif block_type == 'heading_3':
              content = f"### {rich_text_to_markdown(block['heading_3']['rich_text'])}"
          elif block_type == 'bulleted_list_item':
              content = f"{indent_space}- {rich_text_to_markdown(block['bulleted_list_item']['rich_text'])}"
          elif block_type == 'numbered_list_item':
              content = f"{indent_space}{numbered_list_start_index}. {rich_text_to_markdown(block['numbered_list_item']['rich_text'])}"
              numbered_list_start_index += 1
          elif block_type == 'to_do':
              checked = block['to_do']['checked']
              prefix = "- [x]" if checked else "- [ ]"
              content = f"{indent_space}{prefix} {rich_text_to_markdown(block['to_do']['rich_text'])}"
          elif block_type == 'quote':
              quote_text = rich_text_to_markdown(block['quote']['rich_text'])
              content = '\n'.join([f"{indent_space}> {line}" for line in quote_text.split('\n')])
          elif block_type == 'divider':
              content = f"{indent_space}---"
          elif block_type == 'code':
              language = block['code']['language']
              code = rich_text_to_markdown(block['code']['rich_text'])
              code_block_text = f"```{language}\n{code}\n```"
              content = '\n'.join(f"{indent_space}{line}" for line in code_block_text.split('\n'))
          elif block_type == 'image':
              img_block = block['image']
              img_type = img_block['type']
              if img_type == 'external':
                  url = img_block['external']['url']
                  content = f"{indent_space}![image]({url})"
              elif img_type == 'file':
                  url = img_block['file']['url']
                  filename = os.path.basename(url.split('?')[0])
                  save_path = os.path.join(IMG_DIR, filename)
                  if download_image(url, save_path):
                      content = f"{indent_space}![image](/assets/img/{filename})"
                  else:
                      content = f"{indent_space}<!-- 이미지 다운로드 실패 -->"
          elif block_type == 'toggle':
              summary = rich_text_to_markdown(block['toggle']['rich_text'])
              content = f'{indent_space}<details markdown="1">
  {indent_space}  <summary>{summary}</summary>'
  
          if block.get('has_children'):
              child_blocks_response = notion_client.blocks.children.list(block_id=block['id'])
              child_blocks = child_blocks_response.get('results', [])
              next_indent = indent_level + 1 if block_type in ['bulleted_list_item', 'numbered_list_item', 'to_do', 'toggle'] else indent_level
              child_markdown = blocks_to_markdown(notion_client, child_blocks, indent_level=next_indent)
              if child_markdown:
                  content += "\n" + child_markdown
  
          if block_type == 'toggle':
              content += f"\n{indent_space}</details>"
  
          if content:
              md_parts.append(content)
  
      separator = "\n\n"
      return separator.join(filter(None, md_parts))
  
  def page_to_markdown(notion_client, page_id):
      paginated_blocks = notion_client.blocks.children.list(block_id=page_id)
      blocks = paginated_blocks.get('results', [])
      return blocks_to_markdown(notion_client, blocks)
  
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
                  f'  - {category}',
              ]
  
              if tags:
                  front_matter_list.append('tags:')
                  for tag in tags:
                      front_matter_list.append(f'  - "{tag}"')
  
              front_matter_list.extend([
                  'excerpt: ""',
                  'toc: true',
                  'toc_sticky: true',
                  'toc_icon: "cog"',
                  'author_profile: true',
                  'mathjax: true',
                  "---"
              ])
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
  
  ```
</details>


또한, 스크립트가 사용하는 라이브러리를 `requirements.txt` 파일에 명시합니다.

- **경로**: `requirements.txt`

```
requests
notion-client
```

## 3단계: GitHub Actions로 자동화하기

동기화 스크립트를 주기적으로 실행하고, 변경 사항이 있을 때 블로그를 자동으로 배포하는 GitHub Actions 워크플로우를 설정합니다.

- **경로**: `.github/workflows/notion-to-jekyll.yml`

<details markdown="1">
  <summary>yml 파일 예시</summary>

  ```yaml
  name: Sync Notion and Deploy
  
  on:
    workflow_dispatch:
    schedule:
      - cron: '*/10 * * * *'
    push:
      branches:
        - main
  
  # Allow one concurrent deploymentconcurrency:
    group: "pages"
    cancel-in-progress: true
  
  jobs:
    sync-notion:
      runs-on: ubuntu-latest
      permissions:
        contents: write
      outputs:
        changes_pushed: ${{ steps.git.outputs.changes_pushed }}
  
      steps:
        - name: Checkout repository
          uses: actions/checkout@v4
  
        - name: Set up Python 3.11
          uses: actions/setup-python@v5
          with:
            python-version: 3.11
  
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
  
        - name: Run Notion to Jekyll script
          id: sync
          env:
            NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
            DATABASE_ID: ${{ secrets.DATABASE_ID }}
          run: python _scripts/sync_notion.py
  
        - name: Commit and push changes
          id: git
          run: |
            git config --global user.name 'github-actions[bot]'
            git config --global user.email 'github-actions[bot]@users.noreply.github.com'
            git add .
            if git status --porcelain | grep -qE "."; then
              git commit -m "chore: Sync posts and images with Notion"
              git push
              echo "changes_pushed=true" >> $GITHUB_OUTPUT
            else
              echo "No changes to commit."
              echo "changes_pushed=false" >> $GITHUB_OUTPUT
            fi
  
    build:
      runs-on: ubuntu-latest
      needs: sync-notion
      if: github.event_name != 'schedule' || needs.sync-notion.outputs.changes_pushed == 'true'
      permissions:
        contents: read
        pages: write
        id-token: write
  
      steps:
        - name: Checkout
          uses: actions/checkout@v4
          with:
            fetch-depth: 0
            submodules: true
  
        - name: Setup Pages
          id: pages
          uses: actions/configure-pages@v4
  
        - name: Setup Ruby
          uses: ruby/setup-ruby@v1
          with:
            ruby-version: 3.3
            bundler-cache: true
  
        - name: Setup Node.js
          uses: actions/setup-node@v4
          with:
            node-version: '18'
  
        - name: Install dependencies
          run: |
            npm install
  
        - name: Build JavaScript
          run: |
            npm run build:js
  
        - name: Build CSS
          run: |
            npm run build:css
  
        - name: Build site
          run: |
            bundle install
            bundle exec jekyll b -d "_site${{ steps.pages.outputs.base_path }}"
          env:
            JEKYLL_ENV: "production"
  
        - name: Test site
          run: |
            bundle exec htmlproofer _site \
            --disable-external \
            --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
  
        - name: Upload site artifact
          uses: actions/upload-pages-artifact@v3
          with:
            path: "_site${{ steps.pages.outputs.base_path }}"
  
    deploy:
      needs: build
      permissions:
        pages: write
        id-token: write
      environment:
        name: github-pages
        url: ${{ steps.deployment.outputs.page_url }}
      runs-on: ubuntu-latest
      steps:
        - name: Deploy to GitHub Pages
          id: deployment
          uses: actions/deploy-pages@v4
  
  ```
</details>

### 워크플로우

- `on`: 워크플로우가 언제 실행될지를 정의합니다.
  - `workflow_dispatch`: 수동으로 실행할 수 있습니다.

  - `schedule`: `cron: '*/10 * * * *'` 설정은 10분마다 워크플로우를 실행합니다.

  - `push`: `main` 브랜치에 푸시될 때 실행됩니다.

- `jobs`: 워크플로우는 두 개의 잡으로 구성됩니다.
  - `sync-notion`:
    1. Python 환경을 설정하고 `requirements.txt`로 의존성을 설치합니다.

    2. `sync_notion.py` 스크립트를 실행합니다. 이때 GitHub Secrets에 저장된 `NOTION_API_KEY`와 `DATABASE_ID`를 환경 변수로 주입합니다.

    3. 스크립트 실행 후 변경된 파일이 있으면 `git` 명령어로 커밋하고 푸시합니다.

    4. 변경 사항이 있었는지 여부를 `outputs`으로 다음 잡에 전달합니다.

  - `build`:
    1. `sync-notion` 잡이 완료된 후에 실행됩니다.

    2. `if` 조건을 통해, 스케줄 실행의 경우 `sync-notion` 잡에서 변경 사항이 있었을 때만 실행되도록 하여 불필요한 빌드를 방지합니다.

    3. Ruby, Node.js 환경을 설정하고 Jekyll 사이트를 빌드합니다.

    4. 빌드된 결과물을 GitHub Pages에 배포하기 위해 아티팩트로 업로드합니다.

- `deploy`: `build` 잡이 성공하면, 아티팩트를 다운로드하여 GitHub Pages에 배포합니다.

- 참고: 찾아보니 GitHub Actions는 정확히 설정한 시간에 동작하지 않는다고 합니다. 저도 배포해보니 매우 랜덤한 시간에 실행이 되는 것 같습니다. 이정도는 감안해야할듯!

## 4단계: GitHub 리포지토리 설정

### GitHub Secrets 설정

워크플로우가 Notion API에 접근할 수 있도록 앞에서 발급받은 API 키와 데이터베이스 ID를 GitHub 리포지토리의 Secrets에 등록해야 합니다.

- 리포지토리의 `Settings` > `Secrets and variables` > `Actions`로 이동합니다.

- 'New repository secret' 버튼을 클릭하여 아래 두 개의 Secret을 추가합니다.
  - `NOTION_API_KEY`: 1단계에서 발급받은 Notion Integration Secret 값

  - `DATABASE_ID`: 1단계에서 확인한 Notion 데이터베이스 ID

## 마무리

이제 Notion 데이터베이스에 글을 작성하고 status를 `Published` 로 변경해보세요. GitHub Actions에서 워크플로우를 직접 실행할 수도 있습니다.

설정에 따라 마크다운 형식이 깨져서 보일 수 있습니다. 이 경우는 custom css 등 추가 설정이 필요하니 그 부분도 참고하시면 좋을 것 같습니다.