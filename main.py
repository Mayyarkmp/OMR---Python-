from math import floor

import cv2
import numpy as np
import json
from Resizer import resize_horz
from Square_Detection import square_detection
from Segmentation import detect_horizontal_lines, segment_image
from Circle_Detection import (
    detect_circles,
    crop_to_circles,
    group_circles_into_rows,
    create_sub_images,
)
from Answer_Detection import process_and_mark_circles
from Bar_Code_Detection import Bar_Code_Detection, Extract_Student_ID
from JsonReader import Read_Json, Extract_Sections, read_Correct_Answers
from Evaluate_Exam import evaluate_exam

import matplotlib.pyplot as plt

true_false_threshold = 0.625
other_threshold = 0.70


def OMR_Proccessor():
    Json_Data = Read_Json("exmp/state (7).json")

    Sections_Name = Extract_Sections(Json_Data)

    correctAnswers = read_Correct_Answers(Json_Data)

    print(f'Sections name " {Sections_Name}')

    image = cv2.imread("exmp/5.png")
    cv2.imshow("final", image)
    squares = []

    all_sized_width = 400
    image = resize_horz(all_sized_width, image)

    squares = square_detection(image)
    # Sort squares by x+y to find the corners
    squares = sorted(squares, key=lambda sq: sq[1] + sq[2])

    # Get the centers of the four corner squares
    centers = []

    for square in squares[:4]:  # We assume the first four are the corners
        _, x, y, w, h = square
        centerX = floor(x + w / 2)
        centerY = floor(y + h / 2)
        centers.append((centerX, centerY))
        # cv2.drawMarker(image, (centerX, centerY), (255, 0, 0), markerType=cv2.MARKER_CROSS,
        #                markerSize=20, thickness=2, line_type=cv2.LINE_AA)

    # Ensure we have exactly 4 centers
    if len(centers) != 4:
        print("Error: Unable to detect four corner squares.")
        # return
    else:
        # Sort centers by y, then by x to find the correct order (top-left, top-right, bottom-left, bottom-right)
        centers = sorted(centers, key=lambda c: (c[1], c[0]))

        top_left, top_right = sorted(centers[:2], key=lambda c: c[0])
        bottom_left, bottom_right = sorted(centers[2:], key=lambda c: c[0])

        # Define the cropping region
        x_min = min(top_left[0], bottom_left[0])
        x_max = max(top_right[0], bottom_right[0])
        y_min = min(top_left[1], top_right[1])
        y_max = max(bottom_left[1], bottom_right[1])

        image = image[y_min:y_max, x_min:x_max]

        lines = None
        try:
            lines = detect_horizontal_lines(image)
            # print(f"lines : {lines}")
        except Exception as e:
            print(e)
        # Draw detected lines for visualization

        # for line in lines:
        #     x1, y1, x2, y2 = line
        #     cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Segment the image based on detected lines

        segments = None
        if lines is not None:
            segments = segment_image(image, lines)

        # Display segments
        All_Answer_Section_list = {}
        if segments is not None:
            for n, segment in enumerate(segments):
                # if segment.shape[0] > 0 and segment.shape[1] > 0:
                #     cv2.imshow(f'Segment {n}', segment)
                # print("barcode testing ")

                if n == 0:
                    desired_width = 1200
                    segment = resize_horz(desired_width, segment)
                    bar_code = Bar_Code_Detection(segment)

                    Student_ID, bar_code_image = Extract_Student_ID(bar_code)
                    print(f"S id {Student_ID}")
                    # cv2.imshow('barcode', bar_code)
                # and n != len(segments) - 2
                elif n != 0:
                    try:
                        if Sections_Name[n - 1] == "essay":
                            segment = segments[n + 1]
                    except Exception as e:
                        continue
                        # Get original dimensions
                    original_height, original_width = segment.shape[:2]

                    # Set the new width or height
                    desired_width = 1200
                    segment = resize_horz(desired_width, segment)

                    circles = detect_circles(segment, n)
                    segment, offset_Y, offset_X = crop_to_circles(segment, circles)

                    if segment is not None:
                        if circles is not None:
                            # Convert the (x, y) coordinates and radius of the circles to integers
                            circles = np.uint16(np.around(circles))

                            # Draw circles on the image
                            for i in circles:
                                i[0] = i[0] - offset_X
                                i[1] = i[1] - offset_Y
                                # Draw the outer circle
                                cv2.circle(segment, (i[0], i[1]), i[2], (0, 255, 0), 1)
                                # Draw the center of the circle
                                cv2.circle(segment, (i[0], i[1]), 2, (0, 0, 255), 1)
                            # cv2.imshow(f'Segment {n}', segment)
                        rows, numRows = group_circles_into_rows(circles)
                        sub_images, numColumns = create_sub_images(segment, rows)

                        try:
                            # sub_images.sort(key=lambda x: (-x[1][0][1],  x[1][0][0]))

                            sub_images.sort(key=lambda x: (x[1][0], -x[1][1]))
                            # sub_images = Order_Answers(sub_images)
                            num_images = len(sub_images)
                            # Calculate the number of rows and columns
                            cols = 3  # Number of columns
                            rows = (
                                num_images + cols - 1
                            ) // cols  # Calculate rows based on the number of columns

                            # Create a figure to hold the subplots
                            fig, axes = plt.subplots(rows, cols, figsize=(30, 30))

                            # Flatten the axes array if it's 2D
                            axes = axes.flatten()

                            num_axes = 0
                            Answer_Section_list = {}
                            for idx, (sub_image, idxs, circles) in enumerate(
                                sub_images
                            ):
                                # print(f"indexes (row, column) {idxs[0] + 1}, {numColumns[idxs[0]] - (idxs[1])}")

                                actualRowIndex = idxs[0] + 1
                                actualColumnIndex = numColumns[idxs[0]] - (idxs[1])

                                questionIndex = (
                                    actualColumnIndex * numRows + actualRowIndex
                                )
                                print(questionIndex)
                                correctSectionAnswers = correctAnswers[
                                    Sections_Name[n - 1]
                                ]

                                if Sections_Name[n - 1] != "essay":
                                    correctQuestionAnswers = correctSectionAnswers[
                                        questionIndex - 1
                                    ]
                                else:
                                    correctQuestionAnswers = []
                                labeled_image, AnswerIndex = process_and_mark_circles(
                                    sub_image,
                                    circles,
                                    true_false_threshold,
                                    other_threshold,
                                    Sections_Name[n - 1],
                                    correctQuestionAnswers,
                                )

                                # Answer_Section_list.update({f'Question -{questionIndex}-': AnswerIndex})
                                Answer_Section_list.update({questionIndex: AnswerIndex})
                                # Sorting the dictionary by key values
                                # Sorting the dictionary by key values

                                label = idx + 1

                                axes[idx].imshow(labeled_image)
                                axes[idx].set_title(f"Question {idx + 1}")
                                axes[idx].axis("off")
                                num_axes = num_axes + 1
                            Answer_Section_list = dict(
                                sorted(Answer_Section_list.items())
                            )
                            print(Answer_Section_list)
                            All_Answer_Section_list.update(
                                {f"{Sections_Name[n - 1]}": Answer_Section_list}
                            )
                            # Hide any remaining empty subplots
                            for j in range(num_axes, len(axes)):
                                axes[j].axis("off")

                            # cv2.imshow(f'Sub Image {label}, in section {n}', labeled_image)
                            # Show the plot

                            plt.tight_layout()
                            plt.show()

                        except Exception as e:
                            print(f"error {e}-{n}")
        print(f"Answer Dict: {All_Answer_Section_list}")
        studentResult = evaluate_exam(All_Answer_Section_list, Json_Data)
        print(f"Student Result: {json.dumps(studentResult)}")
    # Display the result
    cv2.imshow("final", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    OMR_Proccessor()
