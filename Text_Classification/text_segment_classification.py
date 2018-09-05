import string
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def get_features(data_feature):
    feature_vector = []
    for para in data_feature:
        vector = []

        # spaces to length ratio
        spaces = 0
        length = 0
        for a in range(len(para)):
            spaces += para[a].count(' ')
            length += len(para[a])
        vector.append(float(spaces) / length)

        # number to length ratio
        numbers = 0
        length = 0
        for b in range(len(para)):
            numbers += sum(x.isdigit() for x in para[b])
            length += len(para[b])
        vector.append(float(numbers) / length)

        # alphabet to length ratio
        alpha = 0
        length = 0
        for b in range(len(para)):
            alpha += sum(x.isalpha() for x in para[b])
            length += len(para[b])
        vector.append(float(alpha) / length)

        # uppercase letters to length ratio
        capital = 0
        length = 0
        for c in range(len(para)):
            capital += sum(1 for x in para[c] if x.isupper())
            length += len(para[c])
        vector.append(float(capital) / length)

        # check if the chunk has the same number of leading spaces
        leading = []
        for d in para:
            value = len(d) - len(d.lstrip(' '))
            if value > 0:
                leading.append(value)
        if len(set(leading)) == 1 and len(leading) == len(para):
            vector.append(True)
        else:
            vector.append(False)

        # number of periods
        period = 0
        for e in para:
            period += e.count('.')
        vector.append(period)

        feature_vector.append(vector)

        # ratio of punctuation characters to alphabet characters
        count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
        special_char = 0
        alphabet = 0
        for f in para:
            special_char += count(f, string.punctuation)
            alphabet += count(f, string.ascii_letters)
        if alphabet != 0:
            vector.append(float(special_char) / alphabet)
        else:
            vector.append(float(special_char))

        # sentence starts with this three special characters
        quote = 0
        for g in para:
            if g[0] == ">" or g[0] == ":" or g[0] == "@" or g.split()[0] == "|>":
                quote += 1
            if len(g.split()) > 2:
                if g.split()[1] == ">" or g.split()[1] == "=":
                    quote += 1
                if g.split()[2][0] == "<":
                    quote += 1
            if ">" in g.split()[0]:
                    quote += 1
            else:
                quote += 0
        if quote > 0:
            vector.append(1)
        else:
            vector.append(0)

        # first two characters are "--"
        if para[0][0] == "-" and para[0][1] == "-":
            vector.append(1)
        elif para[0][0] == "-":
            vector.append(1)
        else:
            vector.append(0)

        # it has a number at the beginning
        item = 0
        for h in para:
            value = h.split()[0]
            dot = value[-1:]
            number = value[:(len(value)-1)]
            if number.isdigit() and dot == ".":
                item += 1
            else:
                item += 0
        if item >= 1:
            vector.append(1)
        else:
            vector.append(0)

        # starts with in article
        article = 0
        for k in para:
            if k.split()[0] == "In" and k.split()[1] == "article":
                article += 1
            else:
                article += 0
        if article == 1:
            vector.append(1)
        else:
            vector.append(0)

        # Number of capitalized first characters in a string to word ratio
        caps = 0
        words = 0
        for l in para:
            value = l.split()
            words += len(value)
            for m in value:
                if m[0].isupper():
                    caps += 1
        vector.append(float(caps) / words)

        # average spaces between words
        spaces = []
        for n in para:
            tokens = re.findall('\s+', n)
            for o in range(0, len(tokens)):
                spaces.append(len(tokens[o]))
        avg = 0
        for p in spaces:
            avg += p
        if len(spaces) != 0:
            vector.append(float(avg) / len(spaces))
        else:
            vector.append(float(avg))

        # last character is a period
        last_period = 0
        for q in para:
            if q[-1:] == ".":
                last_period += 1
        vector.append(last_period)

        # average number of words per line
        tab_numb = []
        for r in para:
            table = r.split()
            tab_numb.append(len(table))
        word_avg = 0
        for word_numb in tab_numb:
            word_avg += word_numb
        vector.append(float(word_avg) / len(tab_numb))

        # number of lines the segment consists of
        vector.append(len(para))

    return feature_vector


folder = open("segment/segment.data.train", "r")

data = folder.readlines()

label_list = []
data_list = []
same = []
label_same = []
for line in data:
    if line.split()[0] == "#BLANK#":
        if len(same) != 0:
            tmp = list(same)
            tmp2 = list(label_same)
            data_list.append(tmp)
            label_list.append(label_same[0])
            del same[:]
            del label_same[:]
    else:
        same.append(line.split('\t', 1)[1].strip('\n'))
        label_same.append(line.split()[0])

half = int(len(data_list) * 0.60)

train_data = []
train_label = []
for i in range(half):
    train_data.append(data_list[i])
    train_label.append(label_list[i])

test_data = []
test_label = []
for i in range(half, len(data_list)):
    test_data.append(data_list[i])
    test_label.append(label_list[i])

feature_matrix = get_features(train_data)
test_feature_matrix = get_features(test_data)

model = RandomForestClassifier()

model.fit(feature_matrix, train_label)

predict_labels = model.predict(test_feature_matrix)

# commented out is used for testing
# test = open("output2.txt", "w")

unique_labels = {}
for i in label_list:
    if i not in unique_labels:
        unique_labels[i] = 0

incorrect = 0
for i in range(len(test_label)):
    if test_label[i] != predict_labels[i]:
        incorrect += 1
#         for j in test_data[i]:
#             test.write(test_label[i])
#             test.write("\t")
#             test.write(predict_labels[i])
#             test.write("\t")
#             test.write(j)
#             test.write("\n")
#         test.write("\n")
#
#         for k in unique_labels:
#             if test_label[i] == k:
#                 unique_labels[k] += 1
#
# print unique_labels

correct = len(test_label) - incorrect

accuracy = round(accuracy_score(test_label, predict_labels) * 100, 2)
print "### HW1B ykim160 - OVERALL CORRECT: " + str(correct) + " = " + str(accuracy) + "%" + "\t" \
      + "INCORRECT: " + str(incorrect) + " = " + str(100 - accuracy) + "%"




