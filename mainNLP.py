import spacy
import datetime

class NLP:
    def __init__(self):
        self.phrase = ""
        self.time_elapsed = 0
        self.nlp = spacy.load('en_core_web_sm')

    def get_time_elapsed(self):
        return self.time_elapsed


    def pre_process(self, nlp, phrase):
        # pre_process takes a query phrase as input
        # purpose:
        # remove stop words and punctuations
        # remove the lemma of the words that are not punctuations and stop words
        phrase = nlp(phrase)
        # not token.is_stop and
        text_pre_processed_as_lemma = [token.lemma_ for token in phrase if not token.is_punct]
        # return the list joined as string
        return nlp(' '.join(text_pre_processed_as_lemma))

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

    def get_document_type(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            # try to find the part of the phrase that specifies the type of document or form
            if (token.pos_ == "NOUN" and token.dep_ in ["compound", "dobj"] and token.text in ["document", "form"]):
                # example: transfer exchange form, so the tokens that modify the form are on the left side so add the tokens
                # that are on the left side of the dependency tree and not far from the document or form token in the phrase
                if (token.n_lefts > 0):
                    query.extend([t.text for t in token.lefts if t.pos_ != "VERB" and abs(t.i - token.i) <= 2])
                # if this is left children are empty, then look for tokens on the right side
                # and not far from the document or form token in the phrase
                elif (token.n_rights > 0):
                    query.extend([t.text for t in token.rights if t.pos_ != "VERB" and abs(t.i - token.i) <= 2])
                # else, gather the contents from the subtree that are not self
                else:
                    query.extend([t.text for t in token.subtree if token.text != t.text and abs(t.i - token.i) <= 2])
        return_val = "form_type={}".format(" ".join(query)) if len(query) > 0 else ""
        return return_val

    def get_email(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            if (token.like_email == True):
                query.append(token.text)
        return_val = "email={}".format(" ".join(query)) if len(query) > 0 else ""
        return return_val

    def get_DOB(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            print(token.shape_, token.pos_, token.text)
            # full DOB provided in MM/DD/YYYY format
            if (token.shape_ == "dd/dd/dddd"):
                query.append(token.text)
        return_val = "DOB={}".format(" ".join(query)) if len(query) > 0 else ""
        return return_val

    def get_phone_number(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            # example 8605801212
            if (len(token.text) == 10 and token.shape_ == "dddd" and str(pre_processed_phrase[token.i-2:token.i-1]) in ["phone","number", "phonenumber", "cell"]):
                query.append(token.text)
                break
            # example (860)5801212
            elif (token.shape_ == "ddd)dddd" and str(pre_processed_phrase[token.i-2:token.i-1]) in ["phone","number", "phonenumber", "cell"]):
                query.append(token.text)
                break
            # example 860 580 1212
            elif ((token.shape_ == "ddd" or token.shape_ == "dddd") and token.pos_ == "NUM" and len(list(token.subtree)) == 3 and str(pre_processed_phrase[token.i-2:token.i-1]) in ["phone","number", "phonenumber", "cell"]):
                query.extend([t.text for t in token.subtree])
                break
            # example
            elif ((token.shape_ == "ddd" or token.shape_ == "dddd") and token.pos_ == "NUM" and len(list(token.subtree)) == 2 and str(pre_processed_phrase[token.i-2:token.i-1]) in ["phone","number", "phonenumber", "cell"]):
                query.extend([t.text for t in token.subtree if t.shape_ == "dddd" and len(t.text) > 3])
                break
        return_val = "phone_number={}".format("".join(query)) if len(query) > 0 else ""
        return return_val


    def get_query_from_phrase_test(self, phrase):
        start_time = datetime.datetime.now()
        self.phrase = phrase
        #nlp = spacy.load('en_core_web_sm')
        pre_processed_phrase = self.pre_process(self.nlp, str(self.phrase))
        print(pre_processed_phrase)
        #print("> Attempting to parse : ", pre_processed_phrase)
        query = []
        # for token in pre_processed_phrase:
        #     print(token.text, token.dep_, token.pos_, list(token.children), len(list(token.subtree)))
        #     print("    INFO : Token: ", token.text, " | POS: ", token.pos_, " | Neighbor: ", token.i, " | Dependency: ",
        #           token.dep_, " | LEFTS ", [t.text for t in token.lefts], " | RIGHTS ", [t.text for t in token.rights],
        #           " | subtree: ", list(token.subtree), token.shape_, " | Entity: ", token.ent_type_, " | HEAD: ", token.head, " | ", token.like_email)
        query.append(self.get_document_type(pre_processed_phrase))
        query.append(self.get_email(pre_processed_phrase))
        query.append(self.get_phone_number(pre_processed_phrase))
        query.append(self.get_DOB(pre_processed_phrase))
        #query.append(self.get_SSN_number(pre_processed_phrase))
        end_time = datetime.datetime.now()
        self.time_elapsed = (end_time - start_time).total_seconds()
        # return only non-empty query points
        return [item for item in query if item != '']
