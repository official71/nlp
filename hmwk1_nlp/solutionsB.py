import sys
import nltk
import math
import time
from collections import defaultdict

START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
RARE_SYMBOL = '_RARE_'
RARE_WORD_MAX_FREQ = 5
LOG_PROB_OF_ZERO = -1000


# TODO: IMPLEMENT THIS FUNCTION
# Receives a list of tagged sentences and processes each sentence to generate a list of words and a list of tags.
# Each sentence is a string of space separated "WORD/TAG" tokens, with a newline character in the end.
# Remember to include start and stop symbols in yout returned lists, as defined by the constants START_SYMBOL and STOP_SYMBOL.
# brown_words (the list of words) should be a list where every element is a list of the words of a particular sentence.
# brown_tags (the list of tags) should be a list where every element is a list of the tags of a particular sentence.
def split_wordtags(brown_train):
    brown_words = []
    brown_tags = []

    for bt in brown_train:
        words = [START_SYMBOL, START_SYMBOL]
        tags = [START_SYMBOL, START_SYMBOL]
        for pair in bt.rstrip().split(' '):
            p = pair.rsplit('/', 1)
            words.append(p[0])
            tags.append(p[1])
        words.append(STOP_SYMBOL)
        tags.append(STOP_SYMBOL)
        brown_words.append(words)
        brown_tags.append(tags)

    # print "\nB1 verifications"
    # print brown_words[2335]
    # print brown_tags[2335]

    return brown_words, brown_tags

# Return {item : count} in given list
# Because the list.count() method within for loop is too slow
def count_list_items(lst):
    dd = defaultdict(float)
    for i in lst:
        dd[i] += 1

    return dd

# TODO: IMPLEMENT THIS FUNCTION
# This function takes tags from the training data and calculates tag trigram probabilities.
# It returns a python dictionary where the keys are tuples that represent the tag trigram, and the values are the log probability of that trigram
def calc_trigrams(brown_tags):
    # ngram tuples
    bigram_tuples = []
    trigram_tuples = []
    for bt in brown_tags:
        bigram_tuples.extend(nltk.bigrams(bt))
        trigram_tuples.extend(nltk.trigrams(bt))

    # ngram counts
    bigram_counts = count_list_items(bigram_tuples)
    trigram_counts = count_list_items(trigram_tuples)

    # trigram log probabilities
    q_values = {}
    for t in trigram_counts:
        n = bigram_counts[t[0:2]]
        q_values[t] = math.log(trigram_counts[t]/n, 2) if n else LOG_PROB_OF_ZERO

    # print "\nB2 verifications"
    # print q_values[('*','*','ADJ')]
    # print q_values[('ADJ','.','X')]
    # print q_values[('NOUN','DET','NOUN')]
    # print q_values[('X','.','STOP')]

    return q_values

# This function takes output from calc_trigrams() and outputs it in the proper format
def q2_output(q_values, filename):
    outfile = open(filename, "w")
    trigrams = q_values.keys()
    trigrams.sort()  
    for trigram in trigrams:
        output = " ".join(['TRIGRAM', trigram[0], trigram[1], trigram[2], str(q_values[trigram])])
        outfile.write(output + '\n')
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Takes the words from the training data and returns a set of all of the words that occur more than 5 times (use RARE_WORD_MAX_FREQ)
# brown_words is a python list where every element is a python list of the words of a particular sentence.
# Note: words that appear exactly 5 times should be considered rare!
def calc_known(brown_words):
    unigram_counts = defaultdict(int)
    for bw in brown_words:
        for w in bw:
            unigram_counts[w] += 1

    known_words = set([])
    for w in unigram_counts:
        if unigram_counts[w] > RARE_WORD_MAX_FREQ:
            known_words.add(w)

    return known_words

# TODO: IMPLEMENT THIS FUNCTION
# Takes the words from the training data and a set of words that should not be replaced for '_RARE_'
# Returns the equivalent to brown_words but replacing the unknown words by '_RARE_' (use RARE_SYMBOL constant)
def replace_rare(brown_words, known_words):
    brown_words_rare = []
    for bw in brown_words:
        words = []
        for w in bw:
            if w in known_words:
                words.append(w)
            else:
                words.append(RARE_SYMBOL)
        brown_words_rare.append(words)

    # print "\nB3 verifications"
    # print ' '.join(brown_words_rare[0])
    # print ' '.join(brown_words_rare[1])

    return brown_words_rare

# This function takes the ouput from replace_rare and outputs it to a file
def q3_output(rare, filename):
    outfile = open(filename, 'w')
    for sentence in rare:
        outfile.write(' '.join(sentence[2:-1]) + '\n')
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Calculates emission probabilities and creates a set of all possible tags
# The first return value is a python dictionary where each key is a tuple in which the first element is a word
# and the second is a tag, and the value is the log probability of the emission of the word given the tag
# The second return value is a set of all possible tags for this data set
def calc_emission(brown_words_rare, brown_tags):
    e_values = {}
    taglist = set([])

    # calculate tag counts
    tag_counts = defaultdict(int)
    for bt in brown_tags:
        for t in bt:
            tag_counts[t] += 1

    # taglist
    for t in tag_counts:
        taglist.add(t)

    # calculate emission counts
    e_counts = defaultdict(int)
    for i in range(len(brown_words_rare)):
        wl = brown_words_rare[i]
        tl = brown_tags[i]
        for j in range(len(wl)):
            e_counts[(wl[j], tl[j])] += 1

    # calculate emission log probabilities
    for pair in e_counts:
        e_values[pair] = math.log(float(e_counts[pair])/tag_counts[pair[1]], 2) if tag_counts[pair[1]] else LOG_PROB_OF_ZERO

    # print "\nB4 verifications"
    # print e_values[('America', 'NOUN')]
    # print e_values[('Columbia', 'NOUN')]
    # print e_values[('New', 'ADJ')]
    # print e_values[('York', 'NOUN')]

    return e_values, taglist

# This function takes the output from calc_emissions() and outputs it
def q4_output(e_values, filename):
    outfile = open(filename, "w")
    emissions = e_values.keys()
    emissions.sort()  
    for item in emissions:
        output = " ".join([item[0], item[1], str(e_values[item])])
        outfile.write(output + '\n')
    outfile.close()

def forward(brown_dev_words,taglist, known_words, q_values, e_values):
    probs = []

    for bw in brown_dev_words:
        n = len(bw)

        # pi_list is a list of defaultdict(float), presumably using dict is faster than a 3-d matrix
        # the length of pi_list is n+1, where [0] is for START_SYMBOL
        pi_list = []

        # init, pi(0, *, *) = 1
        pi = defaultdict(float)
        pi[(START_SYMBOL, START_SYMBOL)] = 1
        pi_list.append(pi)

        for k in range(1, n+1):
            # calculate pi(k, S_k, S_k-1) for all possible (S_k, S_k-1)
            pi = defaultdict(float)
            word = bw[k-1] if bw[k-1] in known_words else RARE_SYMBOL

            for tag_k in taglist:
                # of each possible tag S_k, if the emission probability (word, tag) == 0, skip
                e_val = 2 ** e_values[(word, tag_k)] if (word, tag_k) in e_values else 0
                if e_val == 0:
                    continue

                for tag_k_1 in taglist:
                    # for each tag S_k-1, calculate the sum of q(S_k-2, S_k-1, S_k)*pi(k-1, S_k-2, S_k-1) for each possible tag S_K-2
                    sum = float(0)
                    for tag_k_2 in taglist:
                        # q_val_log = q_values.get((tag_k_2, tag_k_1, tag_k), LOG_PROB_OF_ZERO)
                        # q_val = 2 ** q_val_log
                        q_val = 2 ** q_values[(tag_k_2, tag_k_1, tag_k)] if (tag_k_2, tag_k_1, tag_k) in q_values else 0
                        sum += pi_list[k-1][(tag_k_2, tag_k_1)] * q_val

                    # update this pi(k, S_k-1, S_K)
                    pi[(tag_k_1, tag_k)] = sum * e_val

            pi_list.append(pi)

        # the probability of the sentence is sum of pi(n, S_n-1, S_n)*q(S_n-1, S_n, STOP_SYMBOL)
        prob = 0
        for pair in pi_list[n]:
            # q_val_log = q_values.get((pair[0], pair[1], STOP_SYMBOL), LOG_PROB_OF_ZERO)
            # q_val = 2 ** q_val_log
            q_val = 2 ** q_values[(pair[0], pair[1], STOP_SYMBOL)] if (pair[0], pair[1], STOP_SYMBOL) in q_values else 0
            prob += pi_list[n][pair] * q_val

        p = math.log(prob, 2) if prob else LOG_PROB_OF_ZERO
        probs.append(str(p) + '\n')

    # print "\nB5 verifications"
    # print probs[1].rstrip()
    # print probs[2].rstrip()
    # print probs[3].rstrip()
    # print probs[4].rstrip()

    return probs

# This function takes the output of forward() and outputs it to file
def q5_output(tagged, filename):
    outfile = open(filename, 'w')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# This function takes data to tag (brown_dev_words), a set of all possible tags (taglist), a set of all known words (known_words),
# trigram probabilities (q_values) and emission probabilities (e_values) and outputs a list where every element is a tagged sentence 
# (in the WORD/TAG format, separated by spaces and with a newline in the end, just like our input tagged data)
# brown_dev_words is a python list where every element is a python list of the words of a particular sentence.
# taglist is a set of all possible tags
# known_words is a set of all known words
# q_values is from the return of calc_trigrams()
# e_values is from the return of calc_emissions()
# The return value is a list of tagged sentences in the format "WORD/TAG", separated by spaces. Each sentence is a string with a 
# terminal newline, not a list of tokens. Remember also that the output should not contain the "_RARE_" symbol, but rather the
# original words of the sentence!
def viterbi(brown_dev_words, taglist, known_words, q_values, e_values):
    tagged = []

    for bw in brown_dev_words:
        n = len(bw)

        # pi_list is a list of defaultdict(float), presumably using dict is faster than a 3-d matrix
        # the length of pi_list is n+1, where [0] is for START_SYMBOL
        pi_list = []

        # bp_list is a list of dict() for back pointers
        bp_list = []

        # init, pi(0, *, *) = 1
        pi = defaultdict(float)
        pi[(START_SYMBOL, START_SYMBOL)] = 1
        pi_list.append(pi)

        for k in range(1, n+1):
            # calculate pi(k, S_k, S_k-1) for all possible (S_k, S_k-1)
            pi = defaultdict(float)
            bp = {}
            word = bw[k-1] if bw[k-1] in known_words else RARE_SYMBOL

            for tag_k in taglist:
                # of each possible tag S_k, if the emission probability (word, tag) == 0, skip
                e_val = 2 ** e_values[(word, tag_k)] if (word, tag_k) in e_values else 0
                if e_val == 0:
                    continue

                for tag_k_1 in taglist:
                    # for each tag S_k-1, calculate the max of q(S_k-2, S_k-1, S_k)*pi(k-1, S_k-2, S_k-1) for each possible tag S_K-2
                    pi_max = 0
                    tag_max = 'NA'
                    for tag_k_2 in taglist:
                        # q_val_log = q_values.get((tag_k_2, tag_k_1, tag_k), LOG_PROB_OF_ZERO)
                        # q_val = 2 ** q_val_log
                        q_val = 2 ** q_values[(tag_k_2, tag_k_1, tag_k)] if (tag_k_2, tag_k_1, tag_k) in q_values else 0
                        pi_val = pi_list[k-1][(tag_k_2, tag_k_1)] * q_val * e_val
                        if pi_val > pi_max:
                            pi_max = pi_val
                            tag_max = tag_k_2

                    # update this pi(k, S_k-1, S_K)
                    pi[(tag_k_1, tag_k)] = pi_max
                    bp[(tag_k_1, tag_k)] = tag_max

            pi_list.append(pi)
            bp_list.append(bp)

        # find the max of pi(n, S_n-1, S_n)*q(S_n-1, S_n, STOP_SYMBOL)
        pi_max = 0
        pair_max = ('NA', 'NA')
        for pair in pi_list[n]:
            # q_val_log = q_values.get((pair[0], pair[1], STOP_SYMBOL), LOG_PROB_OF_ZERO)
            # q_val = 2 ** q_val_log
            q_val = 2 ** q_values[(pair[0], pair[1], STOP_SYMBOL)] if (pair[0], pair[1], STOP_SYMBOL) in q_values else 0
            pi_val = pi_list[n][pair] * q_val
            if pi_val > pi_max:
                pi_max = pi_val
                pair_max = pair

        # reconstruct the maximum likelihood tag sequence, from tail to head
        tags = [''] * n
        (tag_k_1, tag_k) = pair_max
        tags[n-1] = tag_k
        tags[n-2] = tag_k_1
        for i in range(n-3, -1, -1):
            tag_k_2 = bp_list[i+2].get((tag_k_1, tag_k), 'NA')
            tags[i] = tag_k_2
            tag_k = tag_k_1
            tag_k_1 = tag_k_2

        # tagged sentence
        tagged.append(' '.join(w + '/' + t for (w,t) in zip(bw, tags)) + '\n')
        
    # print "\nB6 verifications"
    # print tagged[0].rstrip()
    # print tagged[1].rstrip()

    return tagged

# This function takes the output of viterbi() and outputs it to file
def q6_output(tagged, filename):
    outfile = open(filename, 'w')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()

# TODO: IMPLEMENT THIS FUNCTION
# This function uses nltk to create the taggers described in question 6
# brown_words and brown_tags is the data to be used in training
# brown_dev_words is the data that should be tagged
# The return value is a list of tagged sentences in the format "WORD/TAG", separated by spaces. Each sentence is a string with a 
# terminal newline, not a list of tokens. 
def nltk_tagger(brown_words, brown_tags, brown_dev_words):
    # Hint: use the following line to format data to what NLTK expects for training
    training = [ zip(brown_words[i],brown_tags[i]) for i in xrange(len(brown_words)) ]

    # IMPLEMENT THE REST OF THE FUNCTION HERE
    default_tagger = nltk.DefaultTagger('NOUN')
    bigram_tagger = nltk.BigramTagger(training, backoff=default_tagger) 
    trigram_tagger = nltk.TrigramTagger(training, backoff=bigram_tagger)

    tagged = []

    for bw in brown_dev_words:
        tagged.append(' '.join(w + '/' + t for (w,t) in trigram_tagger.tag(bw)) + '\n')

    # print "\nB7 verifications"
    # print tagged[0].rstrip()
    # print tagged[1].rstrip()

    return tagged

# This function takes the output of nltk_tagger() and outputs it to file
def q7_output(tagged, filename):
    outfile = open(filename, 'w')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()

DATA_PATH = 'data/'
OUTPUT_PATH = 'output/'

def main():
    # start timer
    time.clock()

    # open Brown training data
    infile = open(DATA_PATH + "Brown_tagged_train.txt", "r")
    brown_train = infile.readlines()
    infile.close()

    # split words and tags, and add start and stop symbols (question 1)
    brown_words, brown_tags = split_wordtags(brown_train)

    # calculate tag trigram probabilities (question 2)
    q_values = calc_trigrams(brown_tags)

    # question 2 output
    q2_output(q_values, OUTPUT_PATH + 'B2.txt')

    # calculate list of words with count > 5 (question 3)
    known_words = calc_known(brown_words)

    # get a version of brown_words with rare words replace with '_RARE_' (question 3)
    brown_words_rare = replace_rare(brown_words, known_words)

    # question 3 output
    q3_output(brown_words_rare, OUTPUT_PATH + "B3.txt")

    # calculate emission probabilities (question 4)
    e_values, taglist = calc_emission(brown_words_rare, brown_tags)

    # question 4 output
    q4_output(e_values, OUTPUT_PATH + "B4.txt")

    # delete unneceessary data
    del brown_train
    del brown_words_rare



    # open Brown development data (question 6)
    infile = open(DATA_PATH + "Brown_dev.txt", "r")
    brown_dev = infile.readlines()
    infile.close()

    # format Brown development data here
    brown_dev_words = []
    for sentence in brown_dev:
        brown_dev_words.append(sentence.split(" ")[:-1])

    # question 5
    forward_probs = forward(brown_dev_words,taglist, known_words, q_values, e_values)
    q5_output(forward_probs, OUTPUT_PATH + 'B5.txt')

    # do viterbi on brown_dev_words (question 6)
    viterbi_tagged = viterbi(brown_dev_words, taglist, known_words, q_values, e_values)

    # question 6 output
    q6_output(viterbi_tagged, OUTPUT_PATH + 'B6.txt')

    # do nltk tagging here
    nltk_tagged = nltk_tagger(brown_words, brown_tags, brown_dev_words)

    # question 7 output
    q6_output(nltk_tagged, OUTPUT_PATH + 'B7.txt')

    # print total time to run Part B
    print "Part B time: " + str(time.clock()) + ' sec'

if __name__ == "__main__": main()
