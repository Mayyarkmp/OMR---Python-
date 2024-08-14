from math import floor
import cv2
import numpy as np


def detect_horizontal_lines(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    # Detect lines using the Hough Line Transform
    image_width = image.shape[1]
    minLineLength = floor(image_width / 1.2)

    # Detect lines using the Hough Transform on the binary image
    lines = cv2.HoughLinesP(~binary, 1, np.pi / 180, threshold=100, minLineLength=minLineLength, maxLineGap=100)

    horizontal_lines = []
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if abs(y1 - y2) < 30:  # This ensures the line is horizontal
                    horizontal_lines.append((x1, y1, x2, y2))

        # Sort lines by their y-coordinate
        horizontal_lines = sorted(horizontal_lines, key=lambda line: line[1])

    return horizontal_lines


def segment_image(image, lines):

    image_height, image_width = image.shape[:2]
    segments = []
    y_coords = [line[1] for line in lines]

    # Sort y_coords to ensure proper segmentation
    y_coords.sort()

    # Add segment from the start of the image to the first line
    if y_coords:
        segments.append(image[0:y_coords[0], :])

    # Add segments between consecutive lines
    for i in range(len(y_coords) - 1):
        y1 = y_coords[i]
        y2 = y_coords[i + 1]
        if abs(y2 - y1) > image_height/30:
            segment = image[y1:y2, :]
            segments.append(segment)

    # Add segment from the last line to the end of the image
    if y_coords:
        segments.append(image[y_coords[-1]:, :])

    return segments
