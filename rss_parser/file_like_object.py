"""A simple file-like object
"""

class FileLikeObject:
    """A simple file-like object

    Written since StringIO has some quirks (e.g. a different
    way to read than 'normal' file-like objects) I decided
    to write a small class that has a file-like interface
    """
    def __init__(self):
        self.__data = ''
        
    def read(self):
        data = self.__data
        self.__data = ''
        return data

    def write(self, value):
        self.__data += value

    def readline(self):
        line = self.__data[self.__data.find('\n'):]
        self.__data = self.__data[:self.__data.find('\n') + 1]
        return line

    def writeline(self, value):
        self.__data += value

    def readlines(self):
        data = ['%s\n' % line for line in self.__data.split('\n')]
        self.__data = ''
        return data

    def writelines(self, lines):
        self.__data += ''.join(lines)

