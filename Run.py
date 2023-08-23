from RecommendationEngine import *
from SimilarityComputation import *
from Validation import *
from data import create_data


if __name__ == '__main__':
    create_data()
    cos_similarity()
    Recommendation().user_based_recommendation()
    generate_test_json()
