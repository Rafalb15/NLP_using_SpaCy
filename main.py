import spacy
import random


def get_input_phrase():
    phrase = ''
    try:
        phrase = input('What are you looking for?: ')
        assert len(phrase) > 1
    except:
        print("There was an issue with your input")
        exit(1)
    finally:
        return phrase


def pre_process(nlp, phrase):
    # pre_process takes a query phrase as input
    # purpose:
    # remove stop words and punctuations
    # remove the lemma of the words that are not punctuations and stop words
    phrase = nlp(phrase)
    text_pre_processed_as_lemma = [token.lemma_ for token in phrase if not token.is_stop and not token.is_punct]
    # return the list joined as string
    return nlp(' '.join(text_pre_processed_as_lemma))


def query_list():
    query_store = []
    query_store.append("return IRA documents from year 2004 and DOB 11/15/1994")
    query_store.append("return W-9 documents where year is 2011")
    query_store.append("return Tax documents where year is 2019")
    query_store.append("return Tax documents where DOB is 11/15/1994 and year is 2004")
    query_store.append("return documents from year 2004 and DOB 11/15/1994")
    random_index = random.randint(0, len(query_store) - 1)
    return query_store


def look_for_nested_child(token):
    # A
    # sequence
    # containing
    # the
    # token and all
    # the
    # token’s
    # syntactic
    # descendants.
    for child in token.subtree:
        print(child.text)


def main():
    nlp = spacy.load('en_core_web_sm')
    # phrase = nlp(get_input_phrase())
    query_store = query_list()

    for q in query_store:

        pre_processed_phrase = pre_process(nlp, q)
        print("> Attempting to parse : ", pre_processed_phrase)
        query = []

        # spacy.displacy.serve(pre_processed_phrase, style='dep')
        for token in pre_processed_phrase:
            #print(token.text, token.dep_, token.pos_, list(token.children), list(token.subtree))
            if (token.dep_ == 'npadvmod'):
                # This relation captures various places where something syntactically a noun phrase (NP) is used as an adverbial modifier in a sentence.
                # look for specific descendants of the word (nested children of children_ to find a year
                temp_string = ' '.join(
                    [child.text for child in token.subtree if
                     child.pos_ == 'NUM' and child.dep_ == 'nummod' and child.shape_ == 'dddd'])
                query.append(token.text + '=' + temp_string)
            if (token.pos_ == 'NOUN' and (token.dep_ == 'compound' or token.dep_ == 'dobj') and len(
                    list(token.children)) > 0):
                temp_string = ' '.join(
                    [child.text for child in token.children if child.pos_ == 'NOUN' or child.pos_ == 'PROPN'])
                query.append(token.text + '=' + temp_string)
            if (token.dep_ == 'appos'):
                # An appositional modifier of an NP is an NP immediately to the right of the first NP that serves to define
                # or modify that NP.
                temp_string = ' '.join([child.text for child in token.rights])
                query.append(token.text + '=' + temp_string)

        print(' \n'.join(qp for qp in query))


if __name__ == "__main__":
    main()
