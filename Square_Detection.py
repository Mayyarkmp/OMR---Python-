import cv2
import numpy as np


def square_detection(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 128, 255,
                              cv2.THRESH_BINARY_INV)  # THRESH_BINARY_INV for white squares on a darker background
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours and filter out squares
    squares = []
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the approximated contour has 4 vertices
        if len(approx) == 4:
            # Check if the contour is convex
            if cv2.isContourConvex(approx):
                # Calculate the area and the bounding rectangle
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)

                # Filter based on aspect ratio and area to ensure it's a square
                aspect_ratio = float(w) / h

                if 0.9 <= aspect_ratio <= 1.1:  # Adjust the area threshold as needed
                    if 200 < area < 240:
                        squares.append([approx, x, y, w, h])

    return squares
