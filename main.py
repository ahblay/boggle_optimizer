from english_words import english_words_lower_alpha_set as wordlist
import json
from pprint import pprint as pp
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable, LpBinary, GUROBI_CMD


'''def search_words(query):
    with open('big_list.json') as f:
        data = json.load(f)
        try:
            return data[query]
        except KeyError:
            return []


def open_word_dict():
    with open('big_list.json') as f:
        data = json.load(f)
    return data, sorted(data.keys())'''


def make_word_dict(dict_filename):
    d = {}
    for word in wordlist:
        ordered = ''.join(sorted(word))
        try:
            d[ordered].append(word)
        except KeyError:
            d[ordered] = []
            d[ordered].append(word)
    with open(f'{dict_filename}.json', 'w') as f:
        json.dump(d, f)


class BoggleOptimizer:
    def __init__(self, w, dict_filename):
        self.model = LpProblem(name='Boggle', sense=LpMinimize)
        self.w = self.sort_words(w)
        self.global_word_dict = self.open_word_dict(dict_filename)

    @staticmethod
    def open_word_dict(dict_filename):
        with open(f'{dict_filename}.json') as f:
            data = json.load(f)
        return data

    @staticmethod
    def sort_words(w):
        return sorted([sorted(l) for l in w])

    '''
    def get_next_entry(self, query):
        idx = 0
        next_key = global_word_list[idx]
        while global_word_list[idx] < query:
            idx += 1
            next_key = global_word_list[idx]
        print(f'next_key: {next_key}')
        print(f'query: {query}')
        for c in range(len(query)):
            if query[c] != next_key[c]:
                return next_key[c]
        return query[-1]'''

    def enumerate_words(self, w, output, current_word):
        # step out if we've used up all the available letters
        if 0 >= len(w):
            return

        # while loop iterates over nested list, appending letters to current word string in alphabetical order
        # when a new letter is appended, it is deleted from w and w is re-sorted alphabetically
        while True:

            # alphabetically first letter is first entry in sorted list w
            new_letter = w[0][0]

            # append nw letter to current candidate word
            new_word = current_word + new_letter

            #print(w)
            #print(new_word)

            # create new letter list that excludes list containing selected letter
            # this action is necessary because boggle cubes cannot be used more than once in a word
            new_w = w[1:]

            # check if current string constitutes a real word
            # if so, append corresponding words to list of output words
            try:
                matches = self.global_word_dict[new_word]
                output += matches
            except KeyError:
                pass

            # step into w, and append a subsequent letter to the current string
            self.enumerate_words(sorted(new_w), output, new_word)

            # if we cannot step in any further, remove last letter from the candidate string and continue looping
            w = new_w + [w[0][1:]]
            w = sorted([l for l in w if l != []])

            # once we have exhausted all possible checks, break out of the while loop
            if len(w) <= 0:
                break
        return list(set(output))

    '''def enumerate_words(w, output, current_word):
        global last_match
        if 0 >= len(w):
            return
        while True:
            new_letter = w[0][0]
            new_word = current_word + new_letter
            print(w)
            print(new_word)
            #next_entry = get_next_entry(new_word)
            #print(f'next_entry: {next_entry}, new_letter: {new_letter}')
            # sort w by new letter
            # new_w = [l for l in w if new_letter not in l]
            new_w = w[1:]
            # print(sorted(new_w))
            if True:
    
                try:
                    matches = global_word_dict[new_word]
                    output += matches
                    #last_match = new_word
                except KeyError:
                    pass
    
                enumerate_words(sorted(new_w), output, new_word)
            w = new_w + [w[0][1:]]
            #w = [[i for i in l if i != new_letter] for l in w]
            w = sorted([l for l in w if l != []])
            #print(w)
            if len(w) <= 0:
                break
        return list(set(output))'''

    def make_vars(self):
        #global global_word_dict
        #global global_word_list
        #global last_match
        #global_word_dict, global_word_list = open_word_dict()
        #last_match = global_word_list[0]
        output = self.enumerate_words(self.w, [], '')
        return output

#make_word_dict()
#open_words()

small_test = [
    ['a', 'c', 'f'],
    ['c', 'c', 'b'],
    ['k', 'g', 'a'],
    ['u', 'o', 'a']
]

med_test = [
    ['a'],
    ['b'],
    ['b'],
    ['c'],
    ['c'],
    ['d'],
    ['h'],
    ['i'],
    ['e'],
    ['k'],
    ['e'],
    ['g'],
    ['g'],
    ['h'],
    ['l'],
    ['i']
]

w = [
    ['a', 'c', 'f', 'g', 'r', 'o'],
    ['c', 'b', 'b', 'h', 'u', 't'],
    ['k', 'g', 'h', 'e', 'a', 's'],
    ['u', 'o', 'e', 'a', 't', 'p']
]

old_boggle = [
    ['a', 'a', 'c', 'i', 'o', 't'],
    ['a', 'b', 'i', 'l', 't', 'y'],
    ['a', 'b', 'j', 'm', 'o', 'qu'],
    ['a', 'c', 'd', 'e', 'm', 'p'],
    ['a', 'c', 'e', 'l', 'r', 's'],
    ['a', 'd', 'e', 'n', 'v', 'z'],
    ['a', 'h', 'm', 'o', 'r', 's'],
    ['b', 'i', 'f', 'o', 'r', 'x'],
    ['d', 'e', 'n', 'o', 's', 'w'],
    ['d', 'k', 'n', 'o', 't', 'u'],
    ['e', 'e', 'f', 'h', 'i', 'y'],
    ['e', 'g', 'k', 'l', 'u', 'y'],
    ['e', 'g', 'i', 'n', 't', 'v'],
    ['e', 'h', 'i', 'n', 'p', 's'],
    ['e', 'l', 'p', 's', 't', 'u'],
    ['g', 'i', 'l', 'r', 'u', 'w']
]


#words = sort_words(med_test)
#output = make_vars(words)

#print(global_word_dict[''.join(sorted('inconsequential'))])

filename = 'big_list'

b = BoggleOptimizer(w, filename)
output = b.make_vars()

output.sort(key=len, reverse=True)

print(output)
print(len(output))
