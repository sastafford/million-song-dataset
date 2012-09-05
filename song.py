import datetime
import hdf5_getters
import logging
import numpy as np
import os
import re
import sys
import time

def die_with_usage():
    """ HELP MENU """
    print 'song.py'
    print 'S. Stafford (2012)'
    print 'translate hdf5 tracks to XML format'
    print 'usage:'
    print '   python song.py [input_dir] [output_dir] <OPT: max>'
    print 'example:'
    print '   python song.py /space/A/A/A /space/out/A/A/A 100'
    sys.exit(0)

def xmlreplace(str):
    return str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\'", "&apos;").replace("\"", "&quot;")

# help menu
if len(sys.argv) < 2:
    die_with_usage()

input_dir = sys.argv[1]
output_dir = sys.argv[2]
#max = sys.argv[3]

if not os.path.isdir(input_dir):
    print input_dir, "does not exist"
    exit()

if not os.path.isdir(output_dir):
    print output_dir, "does not exist"
    exit()

# GLOBAL VARS - need to read in from input
root_dir = "/opt/million-song-dataset"
#exclude_fields = ("get_segments")

#LOGGING
now = datetime.datetime.now().strftime("%Y%m%dT%H%M")

logger = logging.getLogger('song')
logging.basicConfig(filename=root_dir+"/log/song"+now+".log", level=logging.DEBUG)
logger.info("START")

start_time = time.time()

# READ THE TRACK ID/SONG ID MAPPING INTO MEMORY
song_track_file = open(root_dir+"/data/taste_profile_song_to_tracks.txt")
song_track_dict = dict()
for line in song_track_file:
    song_track = re.split(r'[\t]', line)
    if len(song_track) > 1:
        song_track_dict[song_track[0]] = song_track[1][:-1]
    else:
        song_track_dict[line[:-1]] = ""
song_track_file.close()

# Read the evaluation user/songid/listens triplet
user_song_listen_file = open(root_dir+"/data/kaggle_visible_evaluation_triplets.txt")
listen_dict = dict()
for line in user_song_listen_file:
    user_song_listen = re.split(r'[\t]', line)
    song = user_song_listen[1]
    user_listens = [user_song_listen[0], user_song_listen[2][:-1]]
    if song in listen_dict:
        listen_dict[song].append(user_listens)
    else:
        listen_dict[song] = []
        listen_dict[song].append(user_listens)

# get all getters from the hdf5_getters module
getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
getters.remove("get_num_songs") # special case
#getters.remove("get_segments")
getters = np.sort(getters)
print getters

elapsed_time = time.time() - start_time
logger.info("INIT COMPLETE: "+str(elapsed_time))

# LOOP THROUGH THE SONG LIST AND GENERATE XML
songs_file = open(root_dir+"/data/kaggle_songs.txt")
song_order = dict()
for line in songs_file:
    song = re.split(r'[ ]', line)
    song_order[song[0]] = song[1]

outputDir = output_dir
i = 0
hits = 0

for dirpath, dirnames, filenames in os.walk(input_dir):
    for track_file in filenames:
        #print track_file
        #song = re.split(r'[ ]', songs[i])
        output = "<song xmlns=\'http://labrosa.ee.columbia.edu/millionsong/\'>\n"
        h5 = hdf5_getters.open_h5_file_read(os.path.join(dirpath, track_file))
        song_id = hdf5_getters.get_song_id(h5)
        for getter in getters:
            try:
                res = hdf5_getters.__getattribute__(getter)(h5)
            except AttributeError, e:
                continue 
            if res.__class__.__name__ == 'ndarray':
                output = output + "<"+getter[4:]+">"+str(res.shape)+"</"+getter[4:]+">\n"
            else:
                output = output + "<"+getter[4:]+">"+str(res)+"</"+getter[4:]+">\n"
        h5.close()
        if song_id in song_order:
            output = output + "<order>" + song_order[song_id][:-1] + "</order>\n"
            logger.debug(track_file +' HIT')
            hits = hits + 1     
        
        if song_id in listen_dict:
            logger.debug("user listens: " + track_file)
            for user_listen in listen_dict[song_id]:
                output = (output + "<user><user-id>" + user_listen[0] + "</user-id>\n"
                      "<number-of-listens>" + user_listen[1] + "</number-of-listens>\n</user>\n")
        output = output + "</song>"
        dir = outputDir+"/"+track_file[2:3]+"/"+track_file[3:4]+"/"+track_file[4:5]
        if not os.path.exists(dir):
            os.makedirs(dir)
        filename = track_file[:-3] + ".xml"
        f = open(dir+"/"+filename, 'w+')
        f.write(output)
        f.close()
print "SongID Hits:", hits
elapsed_time = time.time() - start_time
print("Elapsed Time: ", elapsed_time)
