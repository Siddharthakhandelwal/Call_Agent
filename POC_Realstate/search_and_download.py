import os
import requests
import logging
from typing import List, Dict
from duckduckgo_search import DDGS #type:ignore
import time
from urllib.parse import urlparse
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def detect_file_type(url: str) -> str:
    """Detect file type from URL"""
    try:
        # First try to detect from URL
        path = urlparse(url).path.lower()
        guess_type = mimetypes.guess_type(path)[0]

        if guess_type:
            if 'pdf' in guess_type:
                return 'pdf'
            elif any(img_type in guess_type for img_type in ['jpeg', 'jpg', 'png']):
                return guess_type.split('/')[-1]

        # If not found, try head request
        response = requests.head(url, headers=HEADERS, allow_redirects=True)
        content_type = response.headers.get('content-type', '').lower()

        if 'pdf' in content_type:
            return 'pdf'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return 'jpg'
        elif 'png' in content_type:
            return 'png'

        return None
    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return None

def download_file(url: str, download_dir: str, index: int) -> Dict:
    """Download a file and return its info"""
    try:
        # Get file type and generate filename
        file_type = detect_file_type(url)
        if not file_type:
            logger.warning(f"Unsupported file type for {url}")
            return None

        # Create safe filename with index to avoid duplicates
        original_name = url.split('/')[-1].split('?')[0]  # Remove query parameters
        base_name = "".join(c for c in original_name if c.isalnum() or c in ('-', '_', '.')).rstrip()
        filename = f"{index}_{base_name}"
        if not filename.endswith(f'.{file_type}'):
            filename = f"{filename}.{file_type}"

        filepath = os.path.join(download_dir, filename)

        # Download file with proper headers
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(filepath)
        logger.info(f"Successfully downloaded: {filename} ({file_size/1024:.1f} KB)")

        return {
            'filename': filename,
            'type': file_type,
            'path': filepath,
            'size': file_size,
            'original_url': url
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        return None

def search_and_download(query: str, download_dir: str = "downloads") -> List[Dict]:
    """Search for files and download them"""
    try:
        # Create download directory
        os.makedirs(download_dir, exist_ok=True)
        downloaded_files = []
        download_index = 1

        # Initialize DuckDuckGo search with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ddgs = DDGS()
                logger.info(f"Searching for: {query}")

                # Search for both web and image results
                web_results = list(ddgs.text(query, max_results=10))
                time.sleep(2)  # Delay between searches
                image_results = list(ddgs.images(query, max_results=10))

                # Process and download PDF results
                for result in web_results:
                    url = result.get('link', '')
                    if url.lower().endswith('.pdf'):
                        file_info = download_file(url, download_dir, download_index)
                        if file_info:
                            downloaded_files.append(file_info)
                            download_index += 1

                # Process and download image results
                for result in image_results:
                    url = result.get('image', '')
                    if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        file_info = download_file(url, download_dir, download_index)
                        if file_info:
                            downloaded_files.append(file_info)
                            download_index += 1

                break  # If successful, break the retry loop

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Search attempt {attempt + 1} failed: {e}")
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"All search attempts failed: {e}")
                    raise

        # Print summary
        if downloaded_files:
            logger.info(f"\nSuccessfully downloaded {len(downloaded_files)} files:")
            for file in downloaded_files:
                logger.info(f"- {file['filename']} ({file['type']}) - Size: {file['size']/1024:.1f} KB")
        else:
            logger.info("No files were downloaded.")

        return downloaded_files

    except Exception as e:
        logger.error(f"Search and download error: {e}")
        return []

def main(query):
    logger.info("Starting search and download...")
    downloaded_files = search_and_download(query)
