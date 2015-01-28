from os import path, listdir
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from config import config
import imghdr

ART_DIR = config.get('Artwork', 'art_path')

def index_art(song):
    ext = path.splitext(song['path'])[1]

    try:
        if ext == '.mp3':
            tags = MP3(song['path'])
        elif ext == '.flac':
            tags = FLAC(song['path'])
        else:
            return None
    except:
        return None

    data = ''

    if isinstance(tags, FLAC) and tags.pictures:
        data = tags.pictures[0].data
    elif isinstance(tags, MP3):
        for tag in tags:
            if tag.startswith('APIC'):
                data = tags[tag].data
                break

    if not data:
        directory = find_art(song)
        if directory:
            try:
                afile = open(directory, 'r')
                data = afile.read()
                afile.close()
            except IOError:
                return None
        else:
            return None

    directory = write_art(song, data)

def find_art(song):
    art_strings = ['cover.jpg', 'cover.png', 'folder.jpg', 'folder.png']
    directory = path.dirname(song['path'])
    for s in art_strings:
        if path.isfile(path.join(directory, s)):
            return path.join(directory, s)

    for f in listdir(directory):
        ext = path.splitext(f)[1]
        if ext == 'jpg' or ext == 'png':
            return path.join(directory, f)

    return None


def write_art(song, data):
    if not data or not song['artist'] or not song['album']:
        return None

    image_type = imghdr.what(None, data)
    ext = ''

    if image_type == 'jpeg':
        ext = '.jpg'
    elif image_type == 'png':
        ext = '.png'

    filepath = u"{0}{1} - {2}{3}".format('.' + ART_DIR, song['artist'], song['album'], ext)
    
    out = open(filepath, 'w')
    out.write(data)
    out.close()


def get_art(artist, album):
    if not album or not artist:
        return None
    ext = ['.jpg', '.png']
    name = artist + " - " + album

    for e in ext:
        if path.isfile('.' + ART_DIR + name + e):
            return '.' + ART_DIR + name + e

    return None