import spacy
import time


def write_query_results_to_file(file_path, query_list):
    if (len(query_list) > 0):
        # open in overwrite mode
        f = open(file_path, "w")
        # if the length of the query list is greater than 0, then write that to the file
        f.write('\n'.join(query_list))
        # close file write
        f.close()
        print("Finished writing content to ", file_path)
    # else:
    # print("Nothing to write")


def query_cleaup(query_list):
    for counter, item in enumerate(query_list):
        print(item)
        print(list(item.split("=")))
        if len(item.split("=")) == 1:
            del query_list[counter]
    return query_list


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
    #  and not token.is_stop
    text_pre_processed_as_lemma = [token.lemma_ for token in phrase if not token.is_punct and not token.is_stop]
    # return the list joined as string
    return nlp(' '.join(text_pre_processed_as_lemma))


def query_list():
    query_store = []
    query_store.append("return W-9 documents where year is 2011")
    query_store.append("return IRA documents with DOB is 11/15/1994 and year is 2004")
    query_store.append("Return API documents SSN is 3123")
    query_store.append("Return W9 documents where phone is 8605801212 and DOB is 11/15/1994")
    query_store.append("Return AIP documents that were handled in 2004 and email is abc@gmail.com")
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


def get_position_in_doc(phrase, word):
    i = len(phrase)
    for token in phrase:
        if (token.text == word):
            i = token.i
            return i


def main():
    nlp = spacy.load('en_core_web_sm')
    # phrase = nlp(get_input_phrase())
    query_store = query_list()

    for q in query_store:

        pre_processed_phrase = pre_process(nlp, q)
        print("> Attempting to parse : ", q)
        query = []

        # spacy.displacy.serve(pre_processed_phrase, style='dep')
        for token in pre_processed_phrase:
            temp_string = ''
            # print(token.text, token.dep_, token.pos_, list(token.children), list(token.subtree))
            # print("    INFO : Token: ", token.text, " | POS: ", token.pos_, " | Neighbor: ", token.i, " | Dependency: ",
            #       token.dep_,
            #       " | subtree: ", list(token.subtree), token.shape_)
            # # pick up type of document that the user wants to return
            if (token.dep_ in ["nsubj", "compound"] and token.pos_ == "NOUN"):
                # Nominal subject: A nominal subject (nsubj) is a nominal which is the syntactic subject and the proto-agent of a clause.
                # token.subtree returns an array of words that are marked as part of the same subtree
                # return PROPN that are at most 1 distance away from their respective noun
                temp_string = ' '.join(
                    [child.text for child in token.subtree if child.pos_ == 'PROPN' and
                     abs(token.i - get_position_in_doc(pre_processed_phrase, child.text)) == 1])
                if (len(temp_string) > 0):
                    query.append(token.text + '=' + temp_string)

            # pick up the SSN number
            if (token.pos_ == "PROPN"):
                # An appositional modifier of an NP is an NP immediately to the right of the first NP that serves to define or modify that NP. I
                temp_string = ' '.join(
                    [child.text for child in token.subtree if child.shape_ == 'dddd' and (len(child.text) in [4, 9])])
                if (len(temp_string) > 0):
                    query.append(token.text + '=' + temp_string)

            # phone number
            if (token.shape_ == 'dddd' and len(token.text) == 10):
                query.append('phone' + '=' + token.text)

            # DOB
            if (token.pos_ == "PROPN"):
                temp_string = ' '.join(
                    [child.text for child in token.subtree if child.shape_ == 'dd/dd/dddd'])
                if (len(temp_string) > 0):
                    query.append(token.text + '=' + temp_string)
            # another way to get DOB
            if (token.pos_ == "NUM" and token.shape_ == "dd/dd/dddd"):
                query.append("DOB=" + token.text)

            # Name
            if (token.pos_ == "PROPN" and token.shape_[0] == "X" and token.shape_[1] == "x" and token.dep_ == "appos"):
                query.append("name=" + token.text)

            # year
            if (token.pos_ == "NUM" and token.shape_ == "dddd" and len(token.text) == 4):
                query.append("year=" + token.text)

            # email
            if (token.text.find("@") != -1):
                query.append("email=" + token.text)


        print("building query... Query below: ")

        file_path = "/Users/rafal/Downloads/lucene-3.6.2 2/input.txt"
        # query_cleaned = query_cleaup(query)
        print("Returned query: ", list(query))
        write_query_results_to_file(file_path, query)

        print("##########################################################")
        time.sleep(2)


if __name__ == "__main__":
    main()
