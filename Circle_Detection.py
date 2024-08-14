import cv2
import numpy as np
from math import floor
from skimage import data, color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte


def detect_circles(image, i):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = img_as_ubyte(image)
    edges = canny(image, sigma=0, low_threshold=40, high_threshold=150, cval=0.9)

    hough_radii = np.arange(14, 20, 1)
    hough_res = hough_circle(edges, hough_radii)

    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, min_xdistance=20, min_ydistance=20,
                                               normalize=True, threshold=0.375)
    circles = []

    for center_y, center_x, radius in zip(cy, cx, radii):
        circles.append([center_x, center_y, radius])

    return circles


def crop_to_circles(segment, circles):
    if not circles:
        return None, None, None

    segment_height, segment_width = segment.shape[:2]

    # Sort circles by x coordinate
    sorted_circles = sorted(circles, key=lambda c: c[0])

    # Get the leftmost and rightmost circles
    start_circle = sorted_circles[0]
    end_circle = sorted_circles[-1]

    # Calculate crop coordinates
    x_start = max(start_circle[0] - start_circle[2], 0)  # Left edge of start circle
    x_end = min(end_circle[0] + end_circle[2], segment_width)  # Right edge of end circle
    y_start = max(min(c[1] - c[2] for c in circles), 0)  # Top edge of highest circle
    y_end = min(max(c[1] + c[2] for c in circles), segment_height)  # Bottom edge of lowest circle

    # Determine the additional width and height to add
    added_width = min(max(floor(segment_width / 45), 20), 25)
    added_height = min(max(floor(segment_height / 45), 20), 25)

    # Adjust the crop coordinates with added width and height, ensuring they stay within bounds
    x_start = max(x_start - added_width, 0)
    x_end = min(x_end + added_width, segment_width)
    y_start = max(y_start - added_height, 0)
    y_end = min(y_end + added_height, segment_height)

    # Crop the image
    cropped_segment = segment[y_start:y_end, x_start:x_end]

    # Calculate removed width from top and left
    removed_top = y_start
    removed_left = x_start

    return cropped_segment, removed_top, removed_left


def group_circles_into_rows(circles, threshold=10):
    rows = []
    circles = sorted(circles, key=lambda x: x[1])  # Sort by y-coordinate

    current_row = [circles[0]]
    for circle in circles[1:]:
        if abs(circle[1] - current_row[-1][1]) <= threshold:
            current_row.append(circle)
        else:
            rows.append(current_row)
            current_row = [circle]
    rows.append(current_row)
    return rows, len(rows)


# Helper function to group circles into columns based on x-coordinates
def group_circles_into_columns(circles, threshold=100):
    columns = []
    circles = sorted(circles, key=lambda x: x[0])  # Sort by x-coordinate

    current_column = [circles[0]]
    for circle in circles[1:]:
        if abs(circle[0] - current_column[-1][0]) <= threshold:
            current_column.append(circle)
        else:
            if current_column:
                columns.append(current_column)
            current_column = [circle]

    if current_column:
        columns.append(current_column)

    return columns


# Function to create sub-images for each column of circles
def create_sub_images(segment, rows_of_circles):
    sub_images = []
    height, width = segment.shape[:2]  # Get the dimensions of the image
    Columns_lens = []
    for row_idx, row in enumerate(rows_of_circles):
        maxColumnLen = 0
        columns = group_circles_into_columns(row)
        for col_idx, column in enumerate(columns):
            # Print each y position of the circles in the column
            # print(f"Y positions in column {col_idx} of row {row_idx}: {[circle[1] for circle in column]}")
            maxColumnLen = col_idx
            x_coords = [circle[0] for circle in column]
            y_coords = [circle[1] for circle in column]

            # Calculate bounding box with clamping to image dimensions
            x_min = max(min(x_coords) - 20, 0)
            x_max = min(max(x_coords) + 50, width)
            y_min = max(min(y_coords) - 20, 0)
            y_max = min(max(y_coords) + 20, height)

            sub_image = segment[y_min:y_max, x_min:x_max]
            sub_image_height, sub_image_width = sub_image.shape[:2]

            if sub_image_width != 0 and sub_image_height != 0:
                # Print each y position before appending
                # print(f"Appending sub-image with Y positions: {[circle[1] for circle in column]}")
                #
                sub_images.append((sub_image, (row_idx, col_idx), [(x - x_min, y - y_min, r) for (x, y, r) in column]))
        Columns_lens.append(maxColumnLen)

    return sub_images, Columns_lens


def Order_Answers(sub_images):
    n = len(sub_images)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Compare by second element (descending)
            if sub_images[j+1][1][1] - sub_images[j][1][1] > 0:
                sub_images[j], sub_images[j + 1] = sub_images[j + 1], sub_images[j]
            # If the second elements are equal, compare by first element (ascending)
            elif 0 < abs(sub_images[j][1][1] - sub_images[j + 1][1][1] ) < 2 and (sub_images[j][1][0] - sub_images[j + 1][1][0]) > 0:
                sub_images[j], sub_images[j + 1] = sub_images[j + 1], sub_images[j]

    return sub_images
