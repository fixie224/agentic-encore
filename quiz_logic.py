def check_answer(user_answer, correct_answer):
    return set(user_answer) == set(correct_answer)

def get_explanation(question_obj):
    return question_obj.get('explanation', 'No explanation provided.')