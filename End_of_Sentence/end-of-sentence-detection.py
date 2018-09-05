from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def get_correct_words(data_list):
    eos = []
    for occ in data_list:
        if occ[0] == "EOS":
            if occ[4] not in eos:
                eos.append(occ[4])
        if occ[0] == "NEOS":
            if occ[4] in eos:
                eos.remove(occ[4])

    return eos


def get_lables(data_list):
    label_vector = []
    for tmp in data_list:
        label_vector.append(tmp[0])

    return label_vector


def get_features(data_list, abbrevs_tmp, titles_tmp, internal_tmp, words):
    feature_vector = []
    for tmp in data_list:
        # 0 = NEOS
        # 1 = EOS
        vector = []

        # left word is an EOS word
        if tmp[4] in words:
            vector.append(1)
        else:
            vector.append(0)

        # left word is in the abbreviation list
        if tmp[4] in abbrevs_tmp:
            vector.append(0)
        else:
            vector.append(1)

        # left word is in the titles list
        if tmp[4] in titles_tmp:
            vector.append(0)
        else:
            vector.append(1)

        # left word is in the sentence internal list
        if tmp[4] in internal_tmp:
            vector.append(0)
        else:
            vector.append(1)

        # word before is shorter than 3 letters
        if len(tmp[4]) < 3:
            vector.append(0)
        else:
            vector.append(1)

        # the first letter of the word before sentence is uppercase
        if tmp[4][0].isupper():
            vector.append(0)
        else:
            vector.append(1)

        # word after sentence is uppercase
        if any(x.isupper() for x in tmp[6]):
            vector.append(1)
        else:
            vector.append(0)

        # left and right words are uppercase
        if tmp[4][0].isupper() and tmp[6][0].isupper():
            vector.append(1)
        else:
            vector.append(0)

        # next word starts with a quotation
        if tmp[6] == '``':
            vector.append(1)
        else:
            vector.append(0)

        # previous word ends with a quotation
        if tmp[4] == "''":
            vector.append(1)
        else:
            vector.append(0)

        # left side words have more than 1 period
        count1 = 0
        for a in range(2, 5):
            count1 += tmp[a].count(".")
        if count1 >= 1:
            vector.append(0)
        else:
            vector.append(1)

        # left side words contains numbers
        for b in range(2, 5):
            if any(y.isdigit() for y in tmp[b]):
                vector.append(0)
                break
            else:
                vector.append(1)
                break

        # sentence is smaller than 1 word
        if int(tmp[9]) < 2:
            vector.append(0)
        else:
            vector.append(1)

        # left side words have length of one
        if len(tmp[2]) == 1 and len(tmp[3]) == 1 and len(tmp[4]) == 1:
            vector.append(0)
        else:
            vector.append(1)

        feature_vector.append(vector)

    return feature_vector


data = open("sent.data.train", "r")
abbrevs = open("classes/abbrevs", "r")
titles = open("classes/titles", "r")
internal = open("classes/sentence_internal", "r")

temp = data.readlines()
half = int(len(temp) * 0.7)


abbrevs_list = []
for line in abbrevs:
    abbrevs_list.append(line.strip())

titles_list = []
for line in titles:
    titles_list.append(line.strip())

internal_list = []
for line in internal:
    internal_list.append(line.strip())

train_data = []
for i in range(half):
    train_data.append(temp[i])

test_data = []
for i in range(half, len(temp)):
    test_data.append(temp[i])

train_data_list = []
for line in train_data:
    one = line.split()
    train_data_list.append(one)

test_data_list = []
for line in test_data:
    one = line.split()
    test_data_list.append(one)

train_words = get_correct_words(train_data_list)
test_words = get_correct_words(test_data_list)

feature_matrix = get_features(train_data_list, abbrevs_list, titles_list, internal_list, train_words)
labels = get_lables(train_data_list)

test_feature_matrix = get_features(test_data_list, abbrevs_list, titles_list, internal_list, test_words)
test_labels = get_lables(test_data_list)

model = RandomForestClassifier()

model.fit(feature_matrix, labels)

predict_labels = model.predict(test_feature_matrix)

# # testing purpose: outputs the incorrect labels to a file
# test = open("output.txt", "w")
#
# counter = 0
# for i in range(len(test_labels)):
#     if test_labels[i] != predict_labels[i]:
#         counter += 1
#         value = test_data_list[i]
#         for j in value:
#             test.write(j)
#             test.write("\t")
#         test.write("\n")
#
# print counter

incorrect = 0
for i in range(len(test_labels)):
    if test_labels[i] != predict_labels[i]:
        incorrect += 1

correct = len(test_labels) - incorrect

accuracy = round(accuracy_score(test_labels, predict_labels) * 100, 2)
print "### HW1A ykim160 - OVERALL CORRECT: " + str(correct) + " = " + str(accuracy) + "%" + "\t" \
      + "INCORRECT: " + str(incorrect) + " = " + str(100 - accuracy) + "%"
