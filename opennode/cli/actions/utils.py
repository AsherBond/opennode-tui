import os, errno
import commands
import ConfigParser
import shutil
from progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, \
                        RotatingMarker, FormatLabel

class CommandException(Exception):
    pass


def mkdir_p(path):
    """Emulates mkdir -p. http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python"""
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno != errno.EEXIST:
            raise
        
def delete(fnm):
    """Delete a filename, suppress exception on a missing file."""
    try:
        os.unlink(fnm)
    except OSError:
        pass

def del_folder(path):
    shutil.rmtree(path)

def get_file_size_bytes(path):
    return int(os.stat(path)[6]) 

def execute(cmd):
    """Run cmd in a shell, return output of the execution. Raise exception for non-0 return code"""
    status, output = commands.getstatusoutput("LC_ALL=C %s" %cmd)
    if status != 0:
        raise CommandException("Failed to execute command '%s'. Status: '%s'. Output: '%s'" 
                               % (cmd, status, output))  
    return output

def calculate_hash(target_file):
    """Hash contents of a file and write hashes out to a file"""
    execute("pfff -k 6996807 -B %s > %s.pfff" % (target_file, target_file))

def execute_in_screen(name, cmd):
    """Create a named screen session and run command there"""
    execute('screen -S %s %s' % (name, cmd))
    
def attach_screen(name):
    """Attached to the named screen session (multi-screen mode)"""
    execute('screen -x -r %s' % name)

class SimpleConfigParser(ConfigParser.ConfigParser):
    """ Parses configuration file without sections. """
    COMMENT_CHAR = '#'
    OPTION_CHAR =  '='
    
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self.options = {}
    
    def get(self, key):
        return self.options[key]
    
    def items(self):
        return self.options
    
    def read(self, filename):
        with open(filename) as configfile:
            for line in configfile:
                # First, remove comments:
                if self.COMMENT_CHAR in line:
                    # split on comment char, keep only the part before
                    line, comment = line.split(self.COMMENT_CHAR, 1)
                # Second, find lines with an option=value:
                if self.OPTION_CHAR in line:
                    # split on option char:
                    option, value = line.split(self.OPTION_CHAR, 1)
                    # strip spaces:
                    option = option.strip()
                    value = value.strip()
                    # store in dictionary:
                    self.options[option] = value


class ConsoleProgressBar(object):
    """A progress bar compatible with urllib download hook"""
    pbar = None
    
    def update_url(self, url):
        if self.pbar.start_time is not None and self.pbar.finished is False:
            self.finish()
        self.pbar.maxval = None

    def __init__(self, tmpl_name):
        self.label = FormatLabel('')
        widgets = [tmpl_name, Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', 
                  ETA(), ' ', FileTransferSpeed()
               ]
        
        self.pbar = ProgressBar(widgets=widgets)

    def download_hook(self, count, blockSize, totalSize):
        if self.pbar.maxval is None: 
            self.pbar.maxval = totalSize
            self.pbar.start()
        self.pbar.update(min(self.pbar.maxval, blockSize * count))
        
    def finish(self):
        self.pbar.finish()
