from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
def hachoir_metadata(filename):
    return extractMetadata(createParser(filename))
