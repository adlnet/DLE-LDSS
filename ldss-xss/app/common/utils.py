from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def antonyms_in_definition(def1, def2):
    lemmatizer = WordNetLemmatizer()
    tokens1 = {lemmatizer.lemmatize(token) for token in word_tokenize(def1.lower()) if token.isalpha()}
    tokens2 = {lemmatizer.lemmatize(token) for token in word_tokenize(def2.lower()) if token.isalpha()}

    def get_antonyms(word):
        return {ant.name() for syn in wn.synsets(word)
                          for lemma in syn.lemmas()
                          for ant in lemma.antonyms()}

    if any(get_antonyms(word) & tokens2 for word in tokens1):
        return True

    if any(get_antonyms(word) & tokens1 for word in tokens2):
        return True

    return False

def preprocess_definition(definition: str)->str:

    if not definition or not isinstance(definition, str):
        raise ValueError("Invalid input: Definition must be a non-empty string.")

    lower_case_definition = definition.lower()
    return lower_case_definition
