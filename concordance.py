import re
import string
from string import ascii_lowercase
import itertools
import collections
import sys
'''
'''
class Concordance:
    '''
    '''
    def __init__(self, common_abbreviations, terminators, wrappers, paragraph):
        self.common_abbreviations = common_abbreviations
        self.terminators = terminators
        self.wrappers = wrappers
        self.paragraph = paragraph


    # Generate list of sentences given the last string index of each sentence.
    def find_sentences(self):
        end = True
        sentences = []
        while end > -1:
            end = self.find_sentence_end()
            if end > -1:
                # Get last sentence of paragraph/text, then remove sentence from text.
                sentences.append(self.paragraph[end:].strip().replace('\n',' '))
                self.paragraph = self.paragraph[:end]
        # Append the first sentence to the end of the list, then reverse it for order preservation.
        sentences.append(self.paragraph)
        sentences.reverse()
        return sentences


    # Find sentence endpoints using sentence terminators/wrappers, and contractions.
    def find_sentence_end(self):
        [possible_endings, contraction_locations] = [[], []]
        contractions = self.common_abbreviations.keys()
        # Define list of valid terminator/wrapper combinations.
        sentence_terminators = self.terminators + [terminator + wrapper for wrapper in self.wrappers for terminator in self.terminators]
        # Given list of valid "sentence_terminators," determine indices of each instance in "paragraph" text.
        for sentence_terminator in sentence_terminators:
            t_indices = list(self.find_all(self.paragraph, sentence_terminator))
            possible_endings.extend(([] if not len(t_indices) else [[i, len(sentence_terminator)] for i in t_indices]))
        # Get the indices for each contraction/abbreviation in text (case insensitive).
        for contraction in contractions:
            c_indices_lower = list(self.find_all(self.paragraph, contraction.lower()))
            c_indices_upper = list(self.find_all(self.paragraph, contraction.upper()))
            c_indices_titled = list(self.find_all(self.paragraph, contraction.title()))
            c_indices = sorted(c_indices_lower + c_indices_upper + c_indices_titled)
            contraction_locations.extend(([] if not len(c_indices) else [i + len(contraction) for i in c_indices]))
        # Re-compute list of possible endings, excluding those at contraction locations.
        possible_endings = [pe for pe in possible_endings if pe[0] + pe[1] not in contraction_locations]
        if len(self.paragraph) in [pe[0] + pe[1] for pe in possible_endings]:
            max_end_start = max([pe[0] for pe in possible_endings])
            possible_endings = [pe for pe in possible_endings if pe[0] != max_end_start]
        # Re-compute list of possible endings, excluding paragraph endpoint.
        # This will be used to determine sentence by sentence, working backward from the end of "paragraph" text.
        possible_endings = [pe[0] + pe[1] for pe in possible_endings if sum(pe) > len(self.paragraph) or (sum(pe) < len(self.paragraph) and self.paragraph[sum(pe)] == ' ')]
        end = (-1 if not len(possible_endings) else max(possible_endings))
        return end


    # Find all of the starting indices for each sentence terminator, and contraction in text.
    def find_all(self, a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1:
                return
            yield start
            start += len(sub)


    # Generate data structure for concordance result
    def build_concordance(self, sentences):
        # Obtain list of unique words from text.
        # Define character exclusions, and remove them from text while preserving periods for abbreviated words.
        exclusions = set(string.punctuation.replace('.',''))
        modified_text = ''.join(ch for ch in ' '.join(sentences) if ch not in exclusions)
        all_items = [word for word in modified_text.split()]
        # Get list abbreviated words in text.
        abbreviated_words = [word for word in all_items if word.lower() in self.common_abbreviations.keys() or word.title() in self.common_abbreviations.keys()]
        # Get list of words, excluding abbreviations.
        temp_unique_words = [word for word in all_items if word.lower() not in self.common_abbreviations.keys() and word.title() not in self.common_abbreviations.keys()]
        # Compute list of unique words using a regular expression, adding back abbreviations, and checking for non-numeric characters in words
        non_unique_words = sorted(list([word.lower() for word in re.compile('\w+').findall(' '.join(temp_unique_words)) + abbreviated_words if not any(char.isdigit() for char in word)]))
        unique_words = sorted(list(set([word.lower() for word in re.compile('\w+').findall(' '.join(temp_unique_words)) + abbreviated_words if not any(char.isdigit() for char in word)])))
        # Create initial data structure for concordance result (excludes sentence numbers in which each word occurance appears).
        concordance_result = [[word, {collections.Counter(non_unique_words)[word]:[]}] for word in unique_words]
        # Determine the sentence numbers in which each word occurrence appears, and include result in final data structure.
        for idx, unique_word_data in enumerate(concordance_result):
            unique_word = concordance_result[idx][0]
            unique_word_count = list(concordance_result[idx][1].keys())[0]
            for idx2, sentence in enumerate(sentences):
                for word in sentence.split():
                    word = ''.join(ch for ch in word if ch not in exclusions).replace(',','')
                    if word.title() not in self.common_abbreviations and word.lower() not in self.common_abbreviations:
                        word = word.replace('.', '')
                    if unique_word.lower() == word.lower():
                        concordance_result[idx][1][unique_word_count].append(idx2 + 1)
        return concordance_result

'''
'''
class PrintedResults():
    '''
    '''
    def __init__(self, concordance_result):
        self.concordance_result = concordance_result
        self.generate_printed_results()


    def generate_printed_results(self):
        self.concordance_result = [[data[0]+':', str(data[1]).strip()] for data in self.concordance_result]
        col_width = max(len(data) for row in self.concordance_result for data in row) + 5
        for idx, row in enumerate(self.concordance_result):
            print(str(''.join(str(data).ljust(col_width) for data in row).replace(']','').replace('[','').replace(', ',',').replace(': ',':')))


if __name__ == '__main__':
    # Define common abbreviations to supplement sentence endpoint detection in text.
    common_abbreviations = {'dr': 'doctor', 'Mr.': 'mister', 'bro.': 'brother', 'bro': 'brother', 'Mrs.': 'mistress', 'Ms.': 'miss', 'Jr.': 'junior', 'Sr.': 'senior',
                 'i.e.': 'for example', 'e.g.': 'for example', 'vs.': 'versus', 'appt.': 'appointment', 'approx.': 'approximately', 'apt.': 'apartment',
                 'A.S.A.P': 'as soon as possible', 'est.': 'established', 'E.T.A': 'estimated time of arrival', 'min.': 'minute', 'misc': 'miscellaneous',
                 'no.': 'number', 'R.S.V.P': 'please make reservation', 'tel.': 'telephone', 'temp.': 'temperature or temporary', 'vet.': 'veteran',
                 'Ave.': 'Avenue', 'Blvd.': 'Boulevard', 'Rd.': 'Road', 'St.': 'Street', 'Dr.': 'Drive'}
    # Define sentence terminators and wrappers, for robust sentence endpoint detection.
    terminators = ['.', '!', '?']
    wrappers = ['"', "'", ')', ']', '}']

    # Read text from arbitrary sample file.
    text = open('sample.txt', 'r').read()

    # Instantiate Concordance object, with abbreviations, terminators, wrappers, and text as constructor arguments.
    concordance = Concordance(common_abbreviations, terminators, wrappers, text)

    # Extract sentences from text via Concordance method find_sentences().
    sentences = [sentence.rstrip() for sentence in concordance.find_sentences()]

    # Build concordance from text and list of sentences.
    concordance_result = concordance.build_concordance(sentences)
    
    # Print concordance results
    printed_results = PrintedResults(concordance_result)