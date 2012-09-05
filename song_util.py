import time
import re
import sys
import os

root_dir = "/opt/million-song-dataset"
output_dir = sys.argv[1]

train_triplets_file = open(root_dir+"/data/train_triplets.txt")
train_triplets = dict()
for line in train_triplets_file:
#for l in range(1, 10):
    #line = train_triplets_file.readline()
    user_song_listen = re.split(r'[\t]', line)
    user_listens = [user_song_listen[0], user_song_listen[2][:-1]]
    song_id = user_song_listen[1]
    song_id_tag = song_id[2:5]
    if song_id_tag in train_triplets:
        if song_id in train_triplets[song_id_tag]:
            train_triplets[song_id_tag][song_id].append(user_listens)
        else:
            train_triplets[song_id_tag][song_id] = []
            train_triplets[song_id_tag][song_id].append(user_listens)
    else:
        train_triplets[song_id_tag] = dict()
        train_triplets[song_id_tag][song_id] = []
        train_triplets[song_id_tag][song_id].append(user_listens)

train_triplets_file.close()   

for key in train_triplets.keys():
    output = "<songs>\n"
    for song in train_triplets[key].keys():
        output = output + "<song>\n"
        dir = "/space/" + key[0:1] + "/" + key[1:2]
        output = output + "\t<song_id>" + song + "</song_id>\n"
        for user in train_triplets[key][song]:
            output = output + "\t<user_id>" + user[0] + "</user_id>\n"
            output = output + "\t<number-of-listens>" + user[1] + "</number-of-listens>\n"
        output = output + "</song>\n"
    output = output + "</songs>"    
    dir = output_dir + "/" + song[2:3] + "/" + song[3:4]
    if not os.path.exists(dir):
        os.makedirs(dir)
    filename = key + ".xml"
    f = open(dir + "/" + filename, 'w+')
    f.write(output)
    f.close()


