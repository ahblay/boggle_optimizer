from english_words import english_words_lower_alpha_set as wordlist
import json
from pprint import pprint as pp
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable, LpBinary, GUROBI_CMD


# creates a JSON object from a word list
# keys are alphabetically ordered strings and values are their English word anagrams
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


# a class for the Boggle LP
class BoggleOptimizer:

    # initializes class variables
    def __init__(self, w, dict_filename):

        # dictionary of Boggle points for words of different lengths
        self.points = {
            1: 0,
            2: 0,
            3: 1,
            4: 1,
            5: 2,
            6: 3,
            7: 5,
            8: 11,
            9: 11,
            10: 11,
            11: 11,
            12: 11,
            13: 11,
            14: 11,
            15: 11,
            16: 11
        }

        # the LP model
        self.model = LpProblem(name='Boggle', sense=LpMinimize)

        # w is the nested list of dice, and cubes stores the letters and the associated dice they belong to
        self.w, self.cubes = self.sort_words(w)

        # opens the JSON dictionary
        self.global_word_dict = self.open_word_dict(dict_filename)

        # creates LP variables from the list of possible words
        self.vars, self.output = self.make_vars()

        # calculates the set of letters adjacent to every letter in every word
        self.neighborhoods = self.total_neighborhoods()

    # opens JSON file
    @staticmethod
    def open_word_dict(dict_filename):
        with open(f'{dict_filename}.json') as f:
            data = json.load(f)
        return data

    # sorts nest list of letters and returns a sorted list and cubes
    @staticmethod
    def sort_words(w):
        s = sorted([sorted(l) for l in w])
        cubes = sorted([sorted([(i, x) for i in w[x]]) for x in range(len(w))])
        print(cubes)
        return s, cubes

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

    # returns the original lists letters belong to after being anagrammed into English words
    def get_permutation_map(self, word):
        results = []
        str_word = ''.join([i[0] for i in word])
        matches = self.global_word_dict[str_word]
        for w in matches:
            helper_1 = [(letter, w.index(letter)) for letter in list(w)]
            helper_1.sort()
            helper_2 = [(helper_1[i][1], word[i][1]) for i in range(len(word))]
            helper_2.sort()
            indices = '.'.join([str(i[1]) for i in helper_2])
            results.append((w, indices))
        return results

    # gets all words that can be formed by selecting at most one letter from each list in w
    def enumerate_words(self, w, output, current_word):
        # step out if we've used up all the available letters
        if 0 >= len(w):
            return

        # while loop iterates over nested list, appending letters to current word string in alphabetical order
        # when a new letter is appended, it is deleted from w and w is re-sorted alphabetically
        while True:

            # alphabetically first letter is first entry in sorted list w
            new_letter = w[0][0]

            # append new letter to current candidate word
            new_word = current_word + [new_letter]

            #print(w)
            #print(new_word)

            # create new letter list that excludes list containing selected letter
            # this action is necessary because boggle cubes cannot be used more than once in a word
            new_w = w[1:]

            # check if current string constitutes a real word
            # if so, append corresponding words to list of output words
            try:
                matches = self.get_permutation_map(new_word)
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

    # creates varaibles from the words in output
    def make_vars(self):
        output = self.enumerate_words(self.cubes, [], [])
        vars = [LpVariable(f'x_{item[0]}_{item[1]}', cat=LpBinary) for item in output]
        return vars, output

    # builds an objective function with the point values as coefficients
    def build_objective(self):
        self.model += lpSum([self.points[len(self.output[i][0])] * self.vars[i] for i in range(len(self.output))])
        print(lpSum([self.points[len(self.output[i][0])] * self.vars[i] for i in range(len(self.output))]))
        return

    # gets the letters that neighbor each letter in a given word
    @staticmethod
    def get_neighborhoods(word):
        neighborhoods = {}
        word_list = list(word[0])
        for l in range(len(word_list)):
            n = []
            if l-1 >= 0:
                 n.append(word_list[l-1])
            if l+1 < len(word_list):
                n.append(word_list[l+1])
            neighborhoods[(word_list[l], int(word[1].split('.')[l]))] = n
        return neighborhoods

    # applies get_neighborhoods() to all words in self.output
    def total_neighborhoods(self):
        n = {}
        for item in self.output:
            new = self.get_neighborhoods(item)
            n[item] = new
            '''for key, val in new.items():
                try:
                    n[key] += val
                    n[key] = list(set(n[key]))
                except KeyError:
                    n[key] = val'''
        print(n)
        return n

    def build_constraints(self):
        # flattens self.cubes
        flat_cubes = [item for sublist in self.cubes for item in sublist]

        # sum of neighbors cannot exceed 8
        for item in flat_cubes:

            # this fails to account for duplicate neighbors, which is a HUGE oversight
            self.model += lpSum([self.vars[self.output.index(key)] * len(self.neighborhoods[key][item]) for key in self.output]) <= 8
        return

#make_word_dict()
#open_words()

# test cases for dice

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

b = BoggleOptimizer(small_test, filename)
vars, output = b.make_vars()

# output.sort(key=len, reverse=True)

print(output)
print(vars)
print(len(output))

b.build_objective()


