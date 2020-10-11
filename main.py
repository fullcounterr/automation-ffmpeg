import os
import argparse
# Watchfolder
import time
import re
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler   

DESTINATION_PATH = ""
SFTP_ENABLED = False

# Do not modify this regex unless you have to.
REGEX = "^(?:\[(.*)\][\s\.])(?:(.+?)[\s\.]-[\s\.])(((?!(1080|720|480)))\d{1,3})[\s\.](?:\[(720p|1080p|480p)\])"
REGEX_CRC = "^(?:\[(.*)\][\s\.])(?:(.+?)[\s\.]-[\s\.])(\d{1,3})[\s\.](?:(\[(1080p|720p|1080p|480p)\])|(\((WEB 1080p|WEB 720p)\))|(\((1080p|720p)\)))(\s|)(?:(\[(.*)\])|(\((.*)\)))"


class FolderNotFoundError(Exception):
    pass

def on_created(event):
    print("File {src} terdeteksi".format(src=event.src_path))
    extension = os.path.splitext(event.src_path)[-1].lower()
    file_name = os.path.basename(event.src_path)
    print(extension)
    print(file_name)
    print(DESTINATION_PATH)

    name = file_name+extension
    l = re.compile(REGEX_CRC).split(name)

    # Check if length is one. If it's one, then it doesn't have CRC. Fall back to non CRC regex.
    if len(l) == 1:
        l = re.compile(REGEX).split(name) 

    # Build new file name
    base = "(Hi10)_"
    file_name = base+re.sub(r"\s+", '_', l[2])+"_-_"+l[3]+"_("+l[1]+")_(720p)"
    print(file_name)
    if extension == ".mkv" or extension == ".mp4" or extension == ".avi":
        print("File is encodeable with ffmpeg. Processing now....")
        if SFTP_ENABLED is True:
            os.system("auto.py -input_file \"{src}\" -hevc -aq_str 0.8 -thread 6 -sftp -apost -destinasi_file  \"{dst}\\{filename}{extension}\"".format(src=event.src_path, extension=extension, filename=file_name, dst=DESTINATION_PATH))
        else:
            os.system("auto.py -input_file \"{src}\" -hevc -aq_str 0.8 -thread 6 -destinasi_file  \"{dst}\\{filename}{extension}\"".format(src=event.src_path, extension=extension, filename=file_name, dst=DESTINATION_PATH))

    else:
        print("File tidak dapat di encode. Lanjut observe...")
        pass
    return True

def on_deleted(event):
    pass

def on_modified(event):
    pass

def on_moved(event):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-spath', type=str, help='lokasi source path yang akan digunakan.')
    parser.add_argument('-dpath', type=str, help='lokasi destination path yang akan digunakan.')
    parser.add_argument('-sftp', action='store_true', help='enable fitur sftp.')
    params = parser.parse_args().__dict__
    if params['spath'] is None:
        raise FolderNotFoundError('Folder tidak ada')
    if params['dpath'] is None:
        raise FolderNotFoundError('Folder tidak ada')
    if params['sftp']:
        SFTP_ENABLED = True
    DESTINATION_PATH = params['dpath']

    # Initiate event handler for file handling
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    handle_event = PatternMatchingEventHandler("*", ignore_patterns, ignore_directories, case_sensitive)
    handle_event.on_created = on_created
    handle_event.on_deleted = on_deleted
    handle_event.on_modified = on_modified
    handle_event.on_moved = on_moved

    # Initiate observer
    observer = Observer()
    #observer.schedule(os.system("auto.py -input_file \"C:\\Kosongan\" -hevc -aq_str 0.8 -destinasi_file \"maksimal.mkv\""), params['path'], recursive=True)
    observer.schedule(handle_event, params['spath'], recursive=False)
    observer.start()
    print("Daemon up and running...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    
