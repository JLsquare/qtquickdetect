import requests

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

