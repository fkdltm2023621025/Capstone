# 2.1에서 윈도우 파일 이름에 포함되면 안되는 문자가 들어간 파일을 다운 받지 못하는 문제를 해결
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def sanitize_filename(filename):
    # 파일 이름에서 허용되지 않는 문자 제거
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def download_images_from_website(url, target_class, download_folder):
    # 폴더가 존재하지 않으면 생성
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # 세션을 생성하여 요청
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # 웹사이트로부터 HTML 콘텐츠를 가져옴
    response = session.get(url, headers=headers)
    response.raise_for_status()  # 요청이 성공했는지 확인

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 지정된 클래스명을 가진 태그를 찾음
    image_tags = soup.find_all(class_=target_class)

    # 찾은 태그들 중에서 이미지를 다운로드
    for tag in image_tags:
        # 태그 내에서 src 속성을 가진 모든 이미지 태그를 찾음
        img_tags = tag.find_all('img')
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url:
                # 절대 경로가 아니라면 URL을 절대 경로로 변환
                img_url = urljoin(url, img_url)

                # 이미지 파일 이름 추출
                parsed_url = urlparse(img_url)
                img_name = os.path.basename(parsed_url.path)
                img_name = sanitize_filename(img_name)

                # 이미지 다운로드
                try:
                    img_data = session.get(img_url, headers=headers).content
                    img_path = os.path.join(download_folder, img_name)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_data)
                    print(f"Downloaded {img_url} to {img_path}")
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")

# 콘솔로부터 입력 받기
url = input("Enter the website URL: ")
target_class = input("Enter the target class name: ")
download_folder = input("Enter the download folder: ")

# 이미지 다운로드 함수 호출
download_images_from_website(url, target_class, download_folder)
