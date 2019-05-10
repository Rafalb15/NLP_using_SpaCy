import spacy
import datetime
# from threading import Thread


class NLP:
    def __init__(self):
        self.phrase = ""
        self.time_elapsed = 0
        self.nlp = spacy.load('en_core_web_sm')

    def get_time_elapsed(self):
        return self.time_elapsed

    def month_string_to_number(self, string):
        m = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12
        }
        s = string.strip()[:3].lower()
        try:
            out = m[s]
            return out
        except:
            print("Cannot convert")
            return string

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

    def get_document_or_form_type(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            # try to find the part of the phrase that specifies the type of document or form
            if (token.pos_ == "NOUN" and token.dep_ in ["compound", "dobj", "nsubj"] and token.text in ["document", "form"]):
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
            # full DOB provided in MM/DD/YYYY format
            # example: born in MM/YY/DDDD
            if (token.shape_ == "dd/dd/dddd" and str(pre_processed_phrase[token.i - 2:token.i - 1]) in ["DOB", "bear"]):
                query.append(token.text)
                break
            # example: born in 1950
            elif (token.shape_ == "dddd" and str(pre_processed_phrase[token.i - 2:token.i - 1]) in ["DOB",
                                                                                                    "bear"] and token.ent_type_ == "DATE"):
                query.append("{}/{}/{}".format("*", "*", token.text))
                break
            # example: born in April 1950
            elif (token.ent_type_ == "DATE" and token.pos_ == "PROPN" and len(list(token.subtree)) == 2):
                month = str(self.month_string_to_number(token.text))
                query.append("{}/{}/{}".format(month, "*", list(token.subtree)[1]))
                break
        return_val = "DOB={}".format(" ".join(query)) if len(query) > 0 else ""
        return return_val

    def get_phone_number(self, pre_processed_phrase):
        query = []
        for token in pre_processed_phrase:
            # example 8605801212
            if (len(token.text) == 10 and token.shape_ == "dddd" and str(
                    pre_processed_phrase[token.i - 2:token.i - 1]) in ["phone", "number", "phonenumber", "cell"]):
                query.append(token.text)
                break
            # example (860)5801212
            elif (token.shape_ == "ddd)dddd" and str(pre_processed_phrase[token.i - 2:token.i - 1]) in ["phone",
                                                                                                        "number",
                                                                                                        "phonenumber",
                                                                                                        "cell"]):
                query.append(token.text.replace(")", ""))
                break
            # example 860 580 1212
            elif ((token.shape_ == "ddd" or token.shape_ == "dddd") and token.pos_ == "NUM" and len(
                    list(token.subtree)) == 3 and str(pre_processed_phrase[token.i - 4:token.i - 3]) in ["phone",
                                                                                                         "number",
                                                                                                         "phonenumber",
                                                                                                         "cell"]):
                query.extend([t.text for t in token.subtree])
                break
        return_val = "phone_number={}".format("".join(query)) if len(query) > 0 else ""
        return return_val

    def get_SSN_or_TIN_number(self, pre_processed_phrase):
        query = []
        type = ""
        for token in pre_processed_phrase:
            if (("SSN" in str(list(token.subtree)) or "TIN" in str(list(token.subtree))) and len(list(token.subtree)) > 2 and "dddd" in [t.shape_ for t in token.subtree]):
                # example SSN is 1231231234
                type = [t.text for t in token.subtree if t.text == "SSN" or t.text == "TIN"][0]
                num = next((t.text for t in token.subtree if len(token.text)==9), None)
                query.append(num)
        return_val = "{}={}".format(type,"".join(query)) if len(query) > 0 else ""
        return return_val

    def get_query_from_phrase_test(self, phrase):
        start_time = datetime.datetime.now()
        self.phrase = phrase
        # nlp = spacy.load('en_core_web_sm')
        pre_processed_phrase = self.pre_process(self.nlp, str(self.phrase))

        query = []
        # for token in pre_processed_phrase:
        #     print(token.text, token.dep_, token.pos_, list(token.children), len(list(token.subtree)))
        #     print("    INFO : Token: ", token.text, " | POS: ", token.pos_, " | Neighbor: ", token.i, " | Dependency: ",
        #           token.dep_, " | LEFTS ", [t.text for t in token.lefts], " | RIGHTS ", [t.text for t in token.rights],
        #           " | subtree: ", list(token.subtree), token.shape_, " | Entity: ", token.ent_type_, " | HEAD: ",
        #           token.head, " | ", token.like_email)
        query.append(self.get_document_or_form_type(pre_processed_phrase))
        query.append(self.get_email(pre_processed_phrase))
        query.append(self.get_phone_number(pre_processed_phrase))
        query.append(self.get_DOB(pre_processed_phrase))
        # query.append(self.get_SSN_or_TIN_number(pre_processed_phrase))
        end_time = datetime.datetime.now()
        # update the time_elapsed for viewers
        self.time_elapsed = (end_time - start_time).total_seconds()
        # return only non-empty query points
        return [item for item in query if item != '']
