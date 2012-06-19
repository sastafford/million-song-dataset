import datetime
import hdf5_getters
import logging
import numpy as np
import os
import re
import time

# GLOBAL VARS - need to read in from input
root_dir = "/cygdrive/c/sandbox/msd"

#LOGGING
now = datetime.datetime.now().strftime("%Y%m%dT%H%M")

logger = logging.getLogger('song')
logging.basicConfig(filename=root_dir+"/log/song"+now+".log", level=logging.DEBUG)
logger.info("START")

start_time = time.time()

# READ THE SONG ID/TRACK ID MAPPING INTO MEMORY
song_track_file = open(root_dir+"/data/taste_profile_song_to_tracks.txt")
song_track_dict = dict()
for line in song_track_file:
    song_track = re.split(r'[\t]', line)
    if len(song_track) > 1:
        song_track_dict[song_track[0]] = song_track[1][:-1]
    else:
        song_track_dict[line[:-1]] = ""

# LOOP THROUGH THE SONG LIST AND GENERATE XML
songs_file = open(root_dir+"/data/kaggle_songs.txt")
songs = songs_file.readlines()

# get all getters from the hdf5_getters module
getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
getters.remove("get_num_songs") # special case
getters = np.sort(getters)

outputDir = root_dir+"/output"
i = 0
hits = 0
# loop through each song and create an xml file
# while (i < len(songs)):
while (i < 1000):
    song = re.split(r'[ ]', songs[i])
    trackid = song_track_dict[song[0]]
    output = (
    "<song xmlns=\'http://labrosa.ee.columbia.edu/millionsong/\'>\n"
    "    <song_id>" + song[0] + "</song_id>\n"
    "    <order>" + song[1][:-1] + "</order>\n"
    "    <track_id>" + trackid + "</track_id>\n"
    )


    track_dir = root_dir+"/data/MillionSongSubset/data/"+trackid[2:3]+"/"+trackid[3:4]+"/"+trackid[4:5]
    track_file = track_dir+"/"+trackid+".h5"
    # Track file check
    if not os.path.isfile(track_file):
        logger.debug(track_file+' does not exist.')
    else:
        logger.debug(song[0] +' HIT')
        h5 = hdf5_getters.open_h5_file_read(track_file)    
        for getter in getters:
            try:
                res = hdf5_getters.__getattribute__(getter)(h5)
            except AttributeError, e:
                continue 
            if res.__class__.__name__ == 'ndarray':
                output = output + "    <"+getter[4:]+">"+str(res.shape)+"</"+getter[4:]+">"
            else:
                output = output + "    <"+getter[4:]+">"+str(res)+"</"+getter[4:]+">"
        h5.close()
        hits = hits + 1
    i = i + 1
    output = output + "</song>"
    dir = outputDir+"/"+song[0][2:3]+"/"+song[0][3:4]+"/"+song[0][4:5]
    if not os.path.exists(dir):
        os.makedirs(dir)
    filename = song[0] + ".xml"
    f = open(dir+"/"+filename, 'w+')
    f.write(output)
    f.close()
print "Hits:", hits
elapsed_time = time.time() - start_time
print("Elapsed Time: ", elapsed_time)