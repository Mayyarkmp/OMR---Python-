import cv2
import numpy as np
from math import floor

def process_and_mark_circles(sub_image, circles, t_f_thr, o_thr, SecName, correctSectionAnswers):
    Indexed_Answers = []
    sub_image_height, sub_image_width = sub_image.shape[:2]  # Get the dimensions of the sub-image

    for index, (x, y, r) in enumerate(circles):
        # Calculate the coordinates for cropping, clamping them within the image boundaries
        x_min = max(x - r, 0)
        x_max = min(x + r, sub_image_width)
        y_min = max(y - r, 0)
        y_max = min(y + r, sub_image_height)

        # Check if the cropped area is valid
        if x_min >= x_max or y_min >= y_max:
            print(f'in index {index} there is {x}, {y},{r} in image size {sub_image_width}, {sub_image_height}')
            print(f"Invalid crop region for circle at index {index}: ({x_min}, {y_min}) to ({x_max}, {y_max})")
            continue

        # Crop the circle from the sub-image
        circle_img = sub_image[y_min:y_max, x_min:x_max]

        # Ensure the cropped image is not empty
        if circle_img.size == 0:
            print(f"Empty image for circle at index {index} with coordinates: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")
            continue

        # Convert to grayscale and apply binary threshold
        gray_circle = cv2.cvtColor(circle_img, cv2.COLOR_BGR2GRAY)
        ret, binary_circle = cv2.threshold(gray_circle, 185, 255, cv2.THRESH_BINARY_INV)

        # Calculate the percentage of black pixels
        total_pixels = binary_circle.size

        # Apply morphological operations
        kernel = np.ones((3, 3), np.uint8)
        binary_circle = cv2.erode(binary_circle, kernel, iterations=2)
        kernel = np.ones((4, 4), np.uint8)
        binary_circle = cv2.dilate(binary_circle, kernel, iterations=1)

        black_pixels = cv2.countNonZero(binary_circle)
        black_percentage = black_pixels / total_pixels

        # Determine the marker color based on the section type
        if SecName == 'bit_question':
            marker_color = (0, 255, 0) if black_percentage >= t_f_thr else (0, 0, 255)
            if black_percentage > t_f_thr:
                Indexed_Answers.append(len(circles) - index - 1)
        else:
            marker_color = (0, 255, 0) if black_percentage >= o_thr else (0, 0, 255)
            if black_percentage > o_thr:
                Indexed_Answers.append(len(circles) - index - 1)

        # Draw the marker on the sub-image
        cv2.circle(sub_image, (x, y), r, marker_color, 2)


    if SecName != 'essay':

        if len(correctSectionAnswers['answers']) != len(Indexed_Answers) and len(Indexed_Answers):
            cv2.drawMarker(sub_image, (floor(sub_image_width - (sub_image_width / 10)), floor(sub_image_height/ 2)), (0, 0, 255), markerType=cv2.MARKER_STAR,
                           markerSize=25, thickness=2, line_type=cv2.LINE_AA)


    if len(Indexed_Answers) == 0:
        cv2.drawMarker(sub_image, (floor(sub_image_width - (sub_image_width / 10)), floor(sub_image_height/ 2)), (200, 100, 255),
                       markerType=cv2.MARKER_STAR,
                       markerSize=25, thickness=2, line_type=cv2.LINE_8)

    return sub_image, Indexed_Answers
