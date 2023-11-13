import requests

def get_content_type(url: str) -> str | None:
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.headers.get('Content-Type', '').split(';')[0].strip()
    except requests.RequestException:
        return None

def is_image(url: str) -> bool:
    content_type = get_content_type(url)
    if not content_type:
        return False
    image_types = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"]
    return content_type in image_types

def is_video(url: str) -> bool:
    content_type = get_content_type(url)
    if not content_type:
        return False
    video_types = ["video/mp4", "video/avi", "video/mkv", "video/mpeg", "video/quicktime", "video/x-msvideo",
                    "video/webm"]
    return content_type in video_types

def is_live_video(url: str) -> bool:
    content_type = get_content_type(url)
    live_content_types = ["application/vnd.apple.mpegurl", "application/dash+xml"]
    live_url_patterns = ["m3u8", ".ts", "live", "streaming"]
    if content_type and content_type in live_content_types:
        return True
    if any(pattern in url for pattern in live_url_patterns):
        return True
    return False