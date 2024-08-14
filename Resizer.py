import cv2
import numpy as np


def resize_horz(desired_width, image):
    original_height, original_width = image.shape[:2]

    # Set the new width or height
    new_width = desired_width
    new_height = int(original_height * (new_width / original_width))
    image = cv2.resize(image, (new_width, new_height))

    return image


def resize_vertical(desired_height, image):
    original_height, original_width = image.shape[:2]

    # Set the new width or height
    new_height = desired_height
    new_width = int(original_width * (new_height / original_height))
    image = cv2.resize(image, (new_width, new_height))

    return image
