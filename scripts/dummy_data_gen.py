import numpy as np
import pandas as pd

def generate_demographic_data(questions, answer_probabilities, n_samples=1000):
    """
    Generate U.S. demographic data based on the provided questions, answer choices, and probabilities.
    
    Parameters:
    - questions: List of questions.
    - answer_probabilities: Dictionary with questions as keys and another dictionary as values. 
                            The nested dictionary should have answer choices as keys and their respective probabilities as values.
    - n_samples: Number of samples to generate.
    
    Returns:
    - A DataFrame with the generated data.
    """
    
    # Validate if all questions in the questions list have a corresponding entry in the answer_probabilities dictionary
    for q in questions:
        if q not in answer_probabilities:
            raise ValueError(f"No answer probabilities provided for the question: {q}")
    
    # Predefined U.S. demographic distributions
    gender_distribution = {
        "Male": 0.49,
        "Female": 0.51
    }
    
    race_distribution = {
        "White": 0.578,
        "Black or African American": 0.124,
        "Asian": 0.059,
        "American Indian": 0.007,
        "Native Hawaiian or Other Pacific Islander": 0.002,
        "Other": 0.03
    }
    
    religion_distribution = {
        "Christianity": 0.65,
        "Judaism": 0.02,
        "Islam": 0.01,
        "Buddhism": 0.01,
        "Hinduism": 0.01,
        "Not Religious": 0.26,
        "Other": 0.04
    }
    
    # Generate data based on the predefined distributions
    gender_data = np.random.choice(list(gender_distribution.keys()), size=n_samples, p=list(gender_distribution.values()))
    race_data = np.random.choice(list(race_distribution.keys()), size=n_samples, p=list(race_distribution.values()))
    religion_data = np.random.choice(list(religion_distribution.keys()), size=n_samples, p=list(religion_distribution.values()))
    
    # Generate data for the provided questions and answers
    data = {
        "gender": gender_data,
        "race": race_data,
        "religion": religion_data
    }
    
    for q in questions:
        answers = np.random.choice(list(answer_probabilities[q].keys()), size=n_samples, p=list(answer_probabilities[q].values()))
        data[q] = answers
    
    return pd.DataFrame(data)

# Example Usage:

questions = ["Your Question Here"]
answer_probabilities = {
    "Your Question Here": {
        "Answer Choice 1": 0.5,
        "Answer Choice 2": 0.5
    }
}

df = generate_demographic_data(questions, answer_probabilities, n_samples=1000)
df.to_csv("output_filename.csv", index=False)
