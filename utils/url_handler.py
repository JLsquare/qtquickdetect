import requests
from typing import Callable

def get_content_type(url: str) -> str | None:
    """
    Gets the content type of a URL
    :param url: URL to check
    :return: Content type of the URL or None if the request failed or the content type is not found
    """

    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.headers.get('Content-Type', '').split(';')[0].strip()
    except requests.RequestException:
        return None

def is_image(url: str) -> bool:
    """
    Convenience function to check if a URL is an image
    :param url: URL to check
    :return: True if the URL points to what is supposed to be an image, False otherwise
    """

    content_type = get_content_type(url)
    if not content_type:
        return False
    image_types = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"]
    return content_type in image_types

def is_video(url: str) -> bool:
    """ 
    Convenience function to check if a URL is a video
    :param url: URL to check
    :return: True if the URL points to what is supposed to be a video, False otherwise
    """

    content_type = get_content_type(url)
    if not content_type:
        return False
    video_types = ["video/mp4", "video/avi", "video/mkv", "video/mpeg", "video/quicktime", "video/x-msvideo",
                    "video/webm"]
    return content_type in video_types

def is_live_video(url: str) -> bool:
    """
    Convenience function to check if a URL is a live video
    :param url: URL to check
    :return: True if the URL points to what is supposed to be a live video, False otherwise
    """

    content_type = get_content_type(url)
    live_content_types = ["application/vnd.apple.mpegurl", "application/dash+xml"]
    live_url_patterns = ["m3u8", ".ts", "live", "streaming"]
    if content_type and content_type in live_content_types:
        return True
    if any(pattern in url for pattern in live_url_patterns):
        return True
    return False

def is_url(url: str) -> bool:
    """
    Convenience function to check if a string is a valid URL
    :param url: String to check
    :return: True if the string is a valid URL, False otherwise
    """

    if not url.startswith('http'):
        return False 

    try:
        requests.head(url, allow_redirects=True, timeout=10)
        return True
    except requests.RequestException:
        return False
    
def download_file(url: str, dst: str, cb: Callable[[int, int], None] | None = None) -> None:
    """
    Downloads a file from a URL
    :param url: URL to download from
    :param dst: Destination path (leading folders must exist)
    :param cb: Callback function to call on download progress (takes current and total bytes as parameters)
    :raises any exception if 
    """

    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    current = 0

    with open(dst, 'wb') as file:
        for chunk in resp.iter_content(chunk_size=1024):
            current += len(chunk)
            print('\r{:%}'.format(current/total), end='')
            file.write(chunk)

            if cb:
                cb(current, total)
                