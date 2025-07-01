def log_result(question_id, correct):
    # Future: simulate tracking to file or database
    print(f"Logged: {question_id} -> {'correct' if correct else 'wrong'}")