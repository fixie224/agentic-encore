import yaml

def load_questions(filepath='data/questions.yaml'):
    with open(filepath, 'r') as file:
        questions = yaml.safe_load(file)
    return questions['questions']