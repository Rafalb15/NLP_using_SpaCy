import spacy


def get_input_phrase():
    phrase = ''
    try:
        phrase = input('What are you looking for?: ')
    except:
        print("There was an issue with your input")
        exit(1)
    finally:
        return phrase


def pre_process(phrase):
    # pre_process takes a query phrase as input
    # purpose:
    # remove stop words and punctuations
    # remove the lemma of the words that are not punctuations and stop words
    text_pre_processed_as_lemma = [token.lemma_.strip() for token in phrase if not token.is_stop and not token.is_punct]
    # return the list joined as string
    return ' '.join(text_pre_processed_as_lemma)


def main():
    nlp = spacy.load('en_core_web_sm')
    phrase = nlp(get_input_phrase())
    pre_processed_phrase = nlp(pre_process(phrase))
    query = []
    for token in pre_processed_phrase:
        print(token.text, token.dep_, token.head.text, token.head.pos_,
              [child for child in token.children])

    # print query contents
    print(' '.join(str(qp) for qp in query))


if __name__ == "__main__":
    main()
