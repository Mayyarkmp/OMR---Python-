import json


def evaluate_exam(student_answers, correct_answers):
    result = {}
    total_correct_marks = 0

    # Extract the sections from the correct answers
    exam_sections = correct_answers['exam_sheet']
    exam_solution = correct_answers['exam_solution']

    for section in student_answers:
        if section not in exam_solution:
            continue

        section_result = {
            "answered_questions": {},
            "correct_marks": 0,
            "total_marks": 0
        }

        # Handle different question types
        if isinstance(exam_solution[section], list):
            correct_answers_list = exam_solution[section]
            for question_num, student_answer in student_answers[section].items():
                # Correct answer for this question
                correct_answer = correct_answers_list[question_num - 1]
                correct_answer_idx = correct_answer['answers']
                degree = correct_answer['degree']

                # Check if the student's answer is correct
                is_correct = student_answer == correct_answer_idx
                section_result["answered_questions"][question_num] = {
                    "student_answer": student_answer,
                    "correct_answer": correct_answer_idx,
                    "is_correct": is_correct
                }

                # Update the marks
                section_result["total_marks"] += degree
                if is_correct:
                    section_result["correct_marks"] += degree

        elif isinstance(exam_solution[section], dict):
            # Special handling for sections like 'essay'
            essay_solution = exam_solution[section]
            for question_num, student_answer in student_answers[section].items():
                # In case of essays, we're just acknowledging the answer
                section_result["answered_questions"][question_num] = {
                    "student_answer": student_answer,
                    "correct_answer": [],  # Essays usually don't have a straightforward correct answer
                    "is_correct": True  # Assume it's correct for the purpose of this example
                }

        # Add the section results
        result[section] = section_result
        total_correct_marks += section_result["correct_marks"]

    # Add the total correct marks to the final result
    result["total_correct_marks"] = total_correct_marks

    return result