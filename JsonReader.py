import json


def Read_Json(jsonPath):
    with open(jsonPath, "r") as file:
        data = json.load(file)

    return data


def Extract_Sections(data):
    examSolutuionsCategories = []
    try:
        CorrectAnswerList = data["exam_solution"]["multiple_choice"]
        print(f"Correct Answers for multiple_choice is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examSolutuionsCategories.append("multiple_choice")
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["bit_question"]
        print(f"Correct Answers for bit_question is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examSolutuionsCategories.append("bit_question")
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["match"]
        print(f"Correct Answers for match is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examSolutuionsCategories.append("match")
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["essay"]
        print(f"Correct Answers for essay is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examSolutuionsCategories.append("essay")
    except Exception as e:
        print(f"Error Read json file with error {e}")

    return examSolutuionsCategories


def read_Correct_Answers(data):
    examCategoriesCorrectAnswers = {}
    try:
        CorrectAnswerList = data["exam_solution"]["multiple_choice"]
        print(f"Correct Answers for multiple_choice is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examCategoriesCorrectAnswers.update({"multiple_choice": CorrectAnswerList})
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["bit_question"]
        print(f"Correct Answers for bit_question is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examCategoriesCorrectAnswers.update({"bit_question": CorrectAnswerList})
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["match"]
        print(f"Correct Answers for match is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examCategoriesCorrectAnswers.update({"match": CorrectAnswerList})
    except Exception as e:
        print(f"Error Read json file with error {e}")
    try:
        CorrectAnswerList = data["exam_solution"]["essay"]
        print(f"Correct Answers for essay is {CorrectAnswerList}")
        if len(CorrectAnswerList) != 0:
            examCategoriesCorrectAnswers.update({"essay": CorrectAnswerList})
    except Exception as e:
        print(f"Error Read json file with error {e}")

    return examCategoriesCorrectAnswers
