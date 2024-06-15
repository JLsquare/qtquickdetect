import random
import cv2 as cv
import numpy as np

from ..models.preset import Preset

# Static resource
FONT = cv.FONT_HERSHEY_SIMPLEX


def draw_bounding_box(img, top_left: tuple[int, int], bottom_right: tuple[int, int], classname: str, class_id: int, confidence: float,
                      preset: Preset) -> None:
    """
    Draws a rectangle, a label with background and a percentage on a loaded openCV image.

    :param img: The input image loaded with OpenCV.
    :param top_left: The top left coordinates of the rectangle.
    :param bottom_right: The bottom right coordinates of the rectangle.
    :param classname: The name of the class.
    :param class_id: The id of the class (used for color generation)
    :param confidence: The confidence of the model.
    :param preset: The associated preset object.
    """
    text_color = preset.text_color
    thickness = preset.box_thickness
    text_size = preset.text_size

    if preset.box_color_per_class:
        box_color = generate_color(class_id)
    else:
        box_color = preset.box_color

    cv.rectangle(img, top_left, bottom_right, box_color, thickness)

    text = '{} : {:.2f}%'.format(classname, confidence * 100)
    (text_width, text_height), _ = cv.getTextSize(text, FONT, text_size, 1)

    text_top_left_y = max(0, top_left[1] - text_height - 9)
    box_coords = ((top_left[0], text_top_left_y - 2), (top_left[0] + text_width + 2, text_top_left_y + text_height + 7))

    cv.rectangle(img, box_coords[0], box_coords[1], box_color, cv.FILLED)
    cv.putText(img, text, (top_left[0], text_top_left_y + text_height), FONT, text_size, text_color,
               1 if text_size < 1 else 2)


def draw_segmentation_mask_from_points(img, mask_points, class_id: int, preset: Preset) -> None:
    """
    Draws a semi-transparent polygon mask on an image.

    :param img: The input image (numpy array).
    :param mask_points: The points of the mask (numpy array).
    :param class_id: The class id (used for color generation).
    :param preset: The associated preset object.
    """
    # mask_color = preset.segment_color
    if preset.segment_color_per_class:
        mask_color = generate_color(class_id)
    else:
        mask_color = preset.segment_color
        
    thickness = preset.segment_thickness

    polygon = np.array([mask_points], dtype=np.int32)

    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    cv.fillPoly(mask, polygon, 255)

    mask_colored = np.zeros(img.shape, dtype=np.uint8)
    mask_colored[:, :] = mask_color[:3] if img.shape[2] == 3 else mask_color[:4]

    img_masked = cv.bitwise_and(mask_colored, mask_colored, mask=mask)

    cv.addWeighted(img, 1, img_masked, 0.5, 0, img)
    cv.polylines(img, polygon, True, mask_color, thickness)


def draw_classification_label(img, class_name: str, confidence: float, preset: Preset,
                              index: int) -> None:
    """
    Draws classification labels on an image.

    :param img: The input image (numpy array).
    :param class_name: The name of the class.
    :param confidence: The confidence of the model.
    :param preset: The associated preset object.
    :param index: The index of the label (Y rank among labels)
    """
    text_color = preset.text_color

    text = '{} : {:.2f}%'.format(class_name, confidence * 100)
    cv.putText(img, text, (10, 30 + 30 * index), FONT, 1, text_color, 2)


def draw_keypoints(img, keypoints: list[tuple[int, int]], preset: Preset) -> None:
    """
    Draws keypoints on an image.
    https://pytorch.org/vision/stable/auto_examples/others/plot_visualization_utils.html#keypoint-output

    :param img: The input image (numpy array).
    :param keypoints: The list of keypoints.
    :param preset: The preset object.
    """
    keypoints = np.array(keypoints)
    skeleton = [
        (0, 1), (0, 2), (1, 3), (2, 4),  # Head
        (5, 6),  # Shoulders
        (5, 11), (6, 12),  # Chest (Shoulders to Hips)
        (5, 7), (7, 9),  # Left Arm
        (6, 8), (8, 10),  # Right Arm
        (11, 12),  # Hips
        (11, 13), (13, 15),  # Left Leg
        (12, 14), (14, 16)  # Right Leg
    ]

    # Group keypoints for color assignment
    head_parts = {0, 1, 2, 3, 4}
    chest_parts = {5, 6, 11, 12}
    left_arm_parts = {7, 9}
    right_arm_parts = {8, 10}
    left_leg_parts = {13, 15}
    right_leg_parts = {14, 16}

    # Draw the keypoints
    for i, keypoint in enumerate(keypoints):
        if tuple(keypoint) != (0, 0):
            center = tuple(keypoint)
            color = None
            if i in head_parts:
                color = preset.pose_head_color
            elif i in chest_parts:
                color = preset.pose_chest_color
            elif i in left_arm_parts:
                color = preset.pose_arm_color
            elif i in right_arm_parts:
                color = preset.pose_arm_color
            elif i in left_leg_parts:
                color = preset.pose_leg_color
            elif i in right_leg_parts:
                color = preset.pose_leg_color
            cv.circle(img, center, preset.pose_point_size, color, cv.FILLED)

    # Draw the skeleton
    for start, end in skeleton:
        if start < len(keypoints) and end < len(keypoints):
            pt1 = tuple(keypoints[start])
            pt2 = tuple(keypoints[end])
            if pt1 != (0, 0) and pt2 != (0, 0):
                color = None
                if {start, end}.intersection(head_parts):
                    color = preset.pose_head_color
                elif ({start, end}.intersection(chest_parts) and not (
                        {start, end}.intersection(left_arm_parts)
                        or {start, end}.intersection(right_arm_parts)
                        or {start, end}.intersection(left_leg_parts)
                        or {start, end}.intersection(right_leg_parts))):
                    color = preset.pose_chest_color
                elif {start, end}.intersection(left_arm_parts):
                    color = preset.pose_arm_color
                elif {start, end}.intersection(right_arm_parts):
                    color = preset.pose_arm_color
                elif {start, end}.intersection(left_leg_parts):
                    color = preset.pose_leg_color
                elif {start, end}.intersection(right_leg_parts):
                    color = preset.pose_leg_color
                cv.line(img, pt1, pt2, color, preset.pose_line_thickness)


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
