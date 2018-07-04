import csv

with open('data.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')
    for row in spamreader:
        print "Number of elements: {}".format(len(row))
        message = row[-1]
        message_type = message.split(":")[1].split(" ")[1]
        message_text = message.split("#lobosjr")[-1].split(":")[-1]
        print message_text
        # if row[-2] is "USERNOTICE":
        #    print "{} is a NOTICE".format(row[-1])
        # print'  '.join(row)