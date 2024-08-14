import cv2
import numpy as np
import zxingcpp


def Bar_Code_Detection(image):
    gray_segment = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding if the image is not already binary
    _, binary = cv2.threshold(gray_segment, 127, 255, cv2.THRESH_BINARY)

    # Define a horizontal kernel for dilation
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))

    # Apply dilation only in the horizontal direction
    dilated = cv2.dilate(~binary, horizontal_kernel, iterations=1)

    # Find contours in the dilated image
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest rectangle contour by area
    largest_contour = max(contours, key=cv2.contourArea)
    # cv2.imshow('largest_contour', largest_contour)
    # Get the bounding box of the largest rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Crop the original image to the bounding box
    bar_code = image[y - 2:y + h + 2, x - 10:x + w + 10]
    # cv2.imshow('bar_code', bar_code)

    return bar_code


def Extract_Student_ID(bar_code):
    Student_ID = ""
    # Read barcodes from the image
    results = zxingcpp.read_barcodes(bar_code)

    for result in results:
        print('Found barcode:'
              f'\n Text:    "{result.text}"'
              f'\n Format:   {result.format}'
              f'\n Content:  {result.content_type}'
              f'\n Position: {result.position}')
        Student_ID = result.text

        # Get image dimensions
        height, width = bar_code.shape[:2]

        # Choose the font and calculate the position for the text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        thickness = 5
        text_size = cv2.getTextSize(Student_ID, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2

        # Put the Student ID as green text in the center of the image
        cv2.putText(bar_code, Student_ID, (text_x, text_y), font, font_scale, (0, 255, 0), thickness)

    if len(results) == 0:
        print("Could not find any barcode.")

    return Student_ID, bar_code
