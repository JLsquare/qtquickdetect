import cv2 as cv

# Static resource
FONT = cv.FONT_HERSHEY_SIMPLEX


def draw_bounding_box(img, top_left: tuple[int, int], bottom_right: tuple[int, int], classname: str, confidence: float,
                      box_color: tuple[int, int, int], text_color: tuple[int, int, int], thickness: int, text_size: float):
    """
    Draws a rectangle, a label with background and a percentage on a loaded openCV image.
    :param img: The input image loaded with OpenCV.
    :param top_left: The top left coordinates of the rectangle.
    :param bottom_right: The bottom right coordinates of the rectangle.
    :param classname: The name of the class.
    :param confidence: The confidence of the model.
    :param box_color: The color of the rectangle.
    :param text_color: The color of the text.
    :param thickness: The thickness of the rectangle lines.
    :param text_size: The size of the text.
    """

    cv.rectangle(img, top_left, bottom_right, box_color, thickness)

    text = '{} : {:.2f}%'.format(classname, confidence * 100)
    (text_width, text_height), _ = cv.getTextSize(text, FONT, text_size, 1)
    box_coords = ((top_left[0], top_left[1]), (top_left[0] + text_width + 2, top_left[1] - text_height - 9))

    cv.rectangle(img, box_coords[0], box_coords[1], box_color, cv.FILLED)
    cv.putText(img, text, (top_left[0], top_left[1] - 5), FONT, text_size, text_color, 2)

