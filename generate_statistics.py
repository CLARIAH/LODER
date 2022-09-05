from collections import Counter
import matplotlib.pyplot as plt


person_prefix = "https://iisg.amsterdam/links/person/"
event_prefix = "https://iisg.amsterdam/links/event/"
event_date = "http://purl.org/vocab/bio/0.1/date"
new_born = "https://iisg.amsterdam/links/vocab/newborn"

f = open("datalegend_reconstructed.nt", "r")

mapping_event_date = {}
mapping_event_person = {}

count = 0
for x in f:
	sts = x.split(" ")
	s = sts[0]
	p = sts[1]
	o = sts[2]
	if event_prefix in s:
		if p == '<' + event_date + '>':
			event_id = int(s[:-1][1:][(len(event_prefix)):])
			date = o[1:][:10]
			mapping_event_date[event_id] = date # do each event have a unique date?
		if p == '<' + new_born + '>' and  person_prefix in o:

			event_id = int(s[:-1][1:][(len(event_prefix)):])

			person_id_string = o[:-1][1:][(len(person_prefix)):]
			if 'i-' in person_id_string:
				person_id = int(person_id_string[2:])
			else:
				person_id = int(person_id_string)
			# [len(event_prefix)]
			# print (s, event_id)
			# print (o , person_id)
			if event_id not in mapping_event_person.keys():
				mapping_event_person[event_id] = [person_id]
			else:
				mapping_event_person[event_id].append(person_id)


print ('how many person are there: ', len (mapping_event_person.values()))
print ('how many birth events are there: ', len (mapping_event_date.keys()))

# a new mapping from person to date_of_birth

mapping_person_DOB = {}
for e in mapping_event_person.keys():
	persons = mapping_event_person[e]
	if event_id in mapping_event_date.keys():
		date = mapping_event_date[event_id]
		for p in persons:
			if p in mapping_person_DOB.keys():
				mapping_person_DOB[p].append (date)
			else:
				mapping_person_DOB[p] = [date]

ct = Counter()
ct2 = Counter()
for p in mapping_person_DOB:
	num_dob = len (mapping_person_DOB[p])

	if len (mapping_person_DOB[p]) > 5:
		print (p)
		print (mapping_person_DOB[p])
	ct[num_dob] += 1
	num_dob2 = len (set(mapping_person_DOB[p]))
	ct2[num_dob2] += 1

# '1804-04-06'

print (ct)

# plot it
# how many person are there:  698284
# how many birth events are there:  1558197
# Counter({1: 515704, 2: 66239, 3: 11856, 4: 2529, 5: 578, 6: 156, 7: 49, 8: 14, 9: 8, 10: 3, 12: 2, 11: 1})
