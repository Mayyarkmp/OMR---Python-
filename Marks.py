import json


def Get_Marks(answers, json):
    # Ground truth, the correct answers and marks to the questions
    Q1mark = json['exam_sheet']['multiple_choice']['default_degree']
    Q2mark = json['exam_sheet']['bit_question']['default_degree']
    Q3mark = json['exam_sheet']['match']['default_degree']
    marks = dict({0: Q1mark}, {1: Q2mark}, {2, Q3mark})
    essayMark = answers['EssayMark']
    
    examSolution = json['examSolution']
    
    # Calculating fullmark
    fullMark = 0
    for i, section in enumerate(answers):
        thisSectionMark = marks[i] # Holds the original mark for each question in the idx section
        for j, question in enumerate(section):
            studentAnswer = answers[section][question]
            correctAnswer = examSolution[section][j]['answers']
            if studentAnswer == correctAnswer:
                fullMark += marks[i] 
    return fullMark        
    
    
    
    