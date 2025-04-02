import os
import requests
import logging
import time
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import mimetypes
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


def create_session_with_retries() -> requests.Session:
    """Create a session with retry mechanism"""
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=1,
                    status_forcelist=[408, 429, 500, 502, 503, 504, 202],
                    allowed_methods=["HEAD", "GET"])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def detect_file_type(url: str, session: requests.Session) -> Optional[str]:
    """Detect file type from URL with improved error handling"""
    try:
        # First try to detect from URL
        path = urlparse(url).path.lower()
        guess_type = mimetypes.guess_type(path)[0]

        if guess_type:
            if 'pdf' in guess_type:
                return 'pdf'
            elif any(img_type in guess_type
                     for img_type in ['jpeg', 'jpg', 'png']):
                return guess_type.split('/')[-1]

        # If not found, try head request
        response = session.head(url,
                                headers=HEADERS,
                                allow_redirects=True,
                                timeout=10)

        # Check for 202 status specifically
        if response.status_code == 202:
            logger.warning(f"Resource not ready (202) for {url}, waiting...")
            time.sleep(2)  # Wait before retry
            response = session.head(url,
                                    headers=HEADERS,
                                    allow_redirects=True,
                                    timeout=10)

        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()

        if 'pdf' in content_type:
            return 'pdf'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return 'jpg'
        elif 'png' in content_type:
            return 'png'

        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error detecting file type for {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error detecting file type for {url}: {str(e)}")
        return None


def download_file(url: str, download_dir: str, index: int,
                  session: requests.Session) -> Optional[Dict]:
    """Download a file with improved error handling and status checking"""
    try:
        file_type = detect_file_type(url, session)
        if not file_type:
            logger.warning(f"Unsupported or undetectable file type for {url}")
            return None

        # Create safe filename
        original_name = url.split('/')[-1].split('?')[0]
        base_name = "".join(c for c in original_name
                            if c.isalnum() or c in ('-', '_', '.')).rstrip()
        filename = f"{index}_{base_name}"
        if not filename.endswith(f'.{file_type}'):
            filename = f"{filename}.{file_type}"

        filepath = os.path.join(download_dir, filename)

        # Download with proper status code handling
        response = session.get(url, headers=HEADERS, stream=True, timeout=15)

        # Handle 202 status specifically
        max_202_retries = 3
        retry_count = 0
        while response.status_code == 202 and retry_count < max_202_retries:
            logger.info(
                f"Received 202 status for {url}, waiting before retry ({retry_count + 1}/{max_202_retries})"
            )
            time.sleep(2 * (retry_count + 1))  # Exponential backoff
            response = session.get(url,
                                   headers=HEADERS,
                                   stream=True,
                                   timeout=15)
            retry_count += 1

        response.raise_for_status()

        # Verify content type after successful response
        content_type = response.headers.get('content-type', '').lower()
        if not any(t in content_type for t in ['image', 'pdf', 'application']):
            logger.warning(f"Unexpected content type {content_type} for {url}")
            return None

        # Download file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            logger.warning(f"Downloaded file is empty: {filename}")
            os.remove(filepath)
            return None

        logger.info(
            f"Successfully downloaded: {filename} ({file_size/1024:.1f} KB)")
        return {
            'filename': filename,
            'type': file_type,
            'path': filepath,
            'size': file_size,
            'original_url': url
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {str(e)}")
        return None


def search_and_download(query: str,
                        download_dir: str = "downloads") -> List[Dict]:
    """Search for files and download them with improved error handling"""
    try:
        os.makedirs(download_dir, exist_ok=True)
        downloaded_files = []
        download_index = 1
        session = create_session_with_retries()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                ddgs = DDGS()
                logger.info(f"Searching for: {query}")

                web_results = list(ddgs.text(query, max_results=10))
                time.sleep(2)
                image_results = list(ddgs.images(query, max_results=10))

                # Process and download PDF results
                for result in web_results:
                    url = result.get('link', '')
                    if url.lower().endswith('.pdf'):
                        file_info = download_file(url, download_dir,
                                                  download_index, session)
                        if file_info:
                            downloaded_files.append(file_info)
                            download_index += 1

                # Process and download image results
                for result in image_results:
                    url = result.get('image', '')
                    if any(url.lower().endswith(ext)
                           for ext in ['.jpg', '.jpeg', '.png']):
                        file_info = download_file(url, download_dir,
                                                  download_index, session)
                        if file_info:
                            downloaded_files.append(file_info)
                            download_index += 1

                break

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Search attempt {attempt + 1} failed: {e}")
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    logger.error(f"All search attempts failed: {e}")
                    raise

        if downloaded_files:
            logger.info(
                f"\nSuccessfully downloaded {len(downloaded_files)} files:")
            for file in downloaded_files:
                logger.info(
                    f"- {file['filename']} ({file['type']}) - Size: {file['size']/1024:.1f} KB"
                )
        else:
            logger.info("No files were downloaded.")

        return downloaded_files

    except Exception as e:
        logger.error(f"Search and download error: {e}")
        return []


def main(query):
    logger.info("Starting search and download...")
    return search_and_download(query)
