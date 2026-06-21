import numpy as np
#!pip install jellyfish
import jellyfish as jf
'''
#METHOD: PART 1 - Find key length
#Try cutting the message into t slices, where each slice contains letters spaced t
#letters apart (test key lengths from 1 - t)
#Find the index of coincidence for each and average the IOCs (IOC = chance that any 2 characters are the same)
#IOC = sum A through Z of (ni (ni - 1) / N (N - 1)) where ni = number of appearances of the letter, and N = slice length
#the key length with the highest IOC = correct key length

'''
def index_of_coincidence(slices):
    letter = "abcdefghijklmnopqrstuvwxyz "
    count = [0] * 27
    total = 0
    numerator = 0

    for char in slices:
        count[letter.index(char)] += 1

    for i in range(27):
        numerator += count[i] * (count[i] - 1)
        total += count[i]

    return 27 * (numerator / (total * (total - 1)))


def keylength(text, max_key_length):
    k = max_key_length
    w = text
    slices = [[]] * (k + 1)
    qd = {}

    for i in range(1, k + 1):
        q = len(w) // (i)
        if (q in qd):
            continue
        else:
            qd[q] = 1

        slices[i] = [""] * (i)

        for slicenumber in range(i):
            l = slicenumber
            while l < len(w):
                slices[i][slicenumber] += w[l]
                l = l + i

    ioc = [[]] * len(slices)

    for i in range(len(slices)):
        ioc[i] = [0] * len(slices[i])
        for j in range(len(slices[i])):
            ioc[i][j] = (index_of_coincidence(slices[i][j]))

    ioc = ioc[1:]
    average_ioc = []  # average value

    for i in ioc:
        if (len(i) == 0):
            continue
        average_ioc.append(sum(i) / len(i))

    key_length = average_ioc.index(max(average_ioc)) + 1

    for i in range(1, len(average_ioc) + 1):
        if (key_length % i == 0):

            if (average_ioc[i - 1] > 1.7):
                key_length = i
                break

    return key_length, slices[key_length]


# part2
# returns a list of size 27, with the percentage frequency of each letter (and  space) in the text
# ind 0-25 -> a-z, 26 = ' '
def make_frequency_table(string):
    strlen = len(string)
    string = string.lower()  # ensure lowercase

    result = []
    for i in range(26):
        result.append(string.count(chr(i + 97)) / strlen)

    result.append(string.count(' ') / strlen)

    return result


# given a frequency table, find the amount of rotations that will result in having the best
# match (least error) with the common english letter frequency table.
def best_rotation(input_table):
    # approximate frequency of english letters
    # ind 0-25 -> [a-z]
    english_distribution = [0.0812, 0.0149, 0.0271, 0.0432, 0.1202, 0.023, 0.0203, 0.0592, 0.0731, 0.001, 0.0069,
                            0.0398, 0.0261, 0.0695, 0.0768, 0.0182, 0.0011, 0.0602, 0.0628, 0.091, 0.0288, 0.0111,
                            0.0209, 0.0017, 0.0211, 0.0007]
    errors = []

    for i in range(27):  # rotate through alphabet and space
        rotated_table = input_table[i:] + input_table[:i]  # rotate array by i
        error = 0

        for i in range(26):  # calculate error by comparing to english distribution (ignore ' ')
            error += abs(rotated_table[i] - english_distribution[i])
        errors.append(error)

    return np.array(errors).argmin()  # return index of minimum error


# slices = 2d list of length keyLength, where each secondary list is a slice of the text
def find_key(slices, keyLength):
    result = []

    slice_distr = []  # 2d array holding frequency of each english letter + space for each slice.
    for slice in slices:
        slice_distr.append(make_frequency_table(slice))

    # for each slice, find the rotation with the least error
    for s in slice_distr:
        result.append(best_rotation(s))
    return result


# part3
# message = encrypted message
# key = array of integers which indicate the amount the message is shifted by
def decipher_message(message, key):
    dict1 = []
    dict2 = []
    # read from both dictionaries
    with open('dict1.txt') as f:
        f.readline()  # Test 1
        f.readline()  # blank line
        for i in range(5):
            f.readline()  # Candidate Text 'i'
            f.readline()  # blank line
            dict1.append(f.readline().strip())
            f.readline()  # blank line

    with open('dict2.txt') as f:
        f.readline()  # Test 2
        f.readline()  # blank line
        line = f.readline()
        dict2.append(line.strip())
        while (line):  # read until end of file
            dict2.append(line.strip())
            line = f.readline()

    # decode message using key
    decoded_message = ""

    keylen = len(key)
    for i in range(len(message)):
        intchar = 26 if message[i] == ' ' else ord(message[i]) - 97  # convert character to integer between 0 and 26
        intchar -= key[i % keylen]  # shift intchar using the key

        intchar = intchar + 27 if intchar < 0 else intchar  # intchar is an integer [0, 26], 26 represents space
        # 0-25 represent letters a through z
        new_char = ' ' if intchar == 26 else chr(intchar + 97)
        decoded_message += new_char

    # check dict1
    for text in dict1:

        # leveneshtein distance = number of insertions/deletions to get from one string to another
        # checks percentage of extra/incorrect characters, counts the text as a match if
        # error% < 15%
        if jf.levenshtein_distance(decoded_message, text) / len(text) < .5:
            return text

    # Check each word in the dictionary, get a similarity score between each
    # word and the next l characters in the reverted text (l = dictionary word #length)
    # Replace the original text message with the corresponding word
    final_message = ""
    index = 0
    decoded_word_array = decoded_message.split(' ')

    for i in range(len(decoded_word_array)):
        word = decoded_word_array[i]
        min_err = float('inf')
        best_word = ""

        for dictword in dict2:
            if index + len(dictword) >= len(decoded_message) or len(dictword) > len(
                    word):  # skip dictword if dictword doesn't fits in the message or if dictword is longer than the word
                continue
            error = jf.levenshtein_distance(word, dictword) / len(dictword)
            if error < min_err:  # if a new best matching word is found, save that word
                min_err = error  # as the new "best match"
                best_word = dictword

        # if the matching word has a high amount of error, a random space may have been encoded, so combine the current
        # word with the next word
        if (best_word == "" or min_err / len(best_word) > .5) and i + 1 < len(decoded_word_array):
            decoded_word_array[i + 1] = word + decoded_word_array[i + 1]
        else:
            # add the best word match to the message and a space
            final_message += best_word
            final_message += ' '

    return final_message


cipher = input("Enter the ciphertext: ")
x = keylength(cipher, 20)
key = find_key(x[1], x[0])
dec = decipher_message(cipher, key)
print("\nMy plaintext guess is: " + dec)

end = input("Press enter to exit")
