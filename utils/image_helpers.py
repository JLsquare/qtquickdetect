import random

import cv2 as cv
import numpy as np

# Static resource
FONT = cv.FONT_HERSHEY_SIMPLEX


def draw_bounding_box(img, top_left: tuple[int, int], bottom_right: tuple[int, int], classname: str, confidence: float,
                      box_color: tuple[int, int, int, int], text_color: tuple[int, int, int, int], thickness: int,
                      text_size: float):
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

    text_top_left_y = max(0, top_left[1] - text_height - 9)
    box_coords = ((top_left[0], text_top_left_y - 2), (top_left[0] + text_width + 2, text_top_left_y + text_height + 7))

    cv.rectangle(img, box_coords[0], box_coords[1], box_color, cv.FILLED)
    cv.putText(img, text, (top_left[0], text_top_left_y + text_height), FONT, text_size, text_color, 1 if text_size < 1 else 2)


def draw_segmentation_mask_from_points(img, mask_points, mask_color: tuple[int, int, int, int]):
    """
    Draws a semi-transparent polygon mask on an image.

    :param img: The input image (numpy array).
    :param mask_points: The points of the mask (numpy array).
    :param mask_color: The color of the mask (R, G, B, A).
    """
    polygon = np.array([mask_points], dtype=np.int32)

    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    cv.fillPoly(mask, polygon, 255)

    mask_colored = np.zeros(img.shape, dtype=np.uint8)
    mask_colored[:, :] = mask_color[:3] if img.shape[2] == 3 else mask_color[:4]

    img_masked = cv.bitwise_and(mask_colored, mask_colored, mask=mask)

    cv.addWeighted(img, 1, img_masked, 0.5, 0, img)


def generate_color(class_id: int) -> tuple[int, int, int, int]:
    """
    Generates a color for a class id.

    :param class_id: The class id.
    :return: The color (R, G, B, A).
    """
    random.seed(class_id)  # Ensure the same color is generated for the same class id

    # Generate a vivid color with at least one channel at full intensity
    channels = [0, 0, 0]
    max_channel = random.randint(0, 2)
    channels[max_channel] = 255  # Set one channel to 255 for vividness

    # Set the other channels to a value between 50 and 200
    for i in range(3):
        if i != max_channel:
            channels[i] = random.randint(50, 200)

    return (*channels, 255)
