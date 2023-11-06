import cv2 as cv
from typing import Tuple, List, Any

# Static resource
FONT = cv.FONT_HERSHEY_SIMPLEX

def draw_bounding_box(img, topleft: Tuple[int, int], bottomright: Tuple[int, int], classname: str, confidence: float, color=(0, 255, 0), thickness=2): 
    """
    Draws a rectangle, a label and a percentage on a loaded openCV image.
    :param img: The input image loaded with OpenCV.
    :param topleft: The top left coordinates of the rectangle.
    :param bottomright: The bottom right coordinates of the rectangle.
    :param classname: The name of the class.
    :param confidence: The confidence of the model.
    :param color: The color of the rectangle.
    :param thickness: The thickness of the rectangle lines.
    """

    cv.rectangle(img, topleft, bottomright, color, thickness)

    text = '{} : {:.2f}%'.format(classname, confidence * 100)
    cv.putText(img, text, topleft, FONT, thickness, color, thickness)


