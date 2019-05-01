import spacy
import datetime

class NLP:
    def __init__(self):
        self.phrase = ""
        self.time_elapsed = 0
        self.nlp = spacy.load('en_core_web_sm')

    def pre_process(self, nlp, phrase):
        # pre_process takes a query phrase as input
        # purpose:
        # remove stop words and punctuations
        # remove the lemma of the words that are not punctuations and stop words
        phrase = nlp(phrase)
        text_pre_processed_as_lemma = [token.lemma_ for token in phrase if not token.is_stop and not token.is_punct]
        # return the list joined as string
        return nlp(' '.join(text_pre_processed_as_lemma))

    def get_position_in_doc(self, phrase, word):
        i = len(phrase)
        for token in phrase:
            if (token.text == word):
                i = token.i
                return i

    def get_query_from_phrase(self, phrase):
        start_time = datetime.datetime.now()
        self.phrase = phrase
        #nlp = spacy.load('en_core_web_sm')
        pre_processed_phrase = self.pre_process(self.nlp, str(self.phrase))
        #print("> Attempting to parse : ", pre_processed_phrase)
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
                     abs(token.i - self.get_position_in_doc(pre_processed_phrase, child.text)) == 1])
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

        end_time = datetime.datetime.now()
        self.time_elapsed = (end_time - start_time).total_seconds()
        return list(query)
