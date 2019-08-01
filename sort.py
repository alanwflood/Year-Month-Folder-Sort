""" Sort files into folders using the structure Year/Month/filename """
import os
import shutil
import datetime
import errno
import argparse
import sys
import glob

def get_date_from_file(filename):
    """ returns timestamp for file """
    return datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)

def create_file_list(directories):
    """ takes a list of directories, returns a list of tuples (file, month, date) """
    files = glob.glob("")
    # Setup correct globs
    for directory in directories:
        for extension in EXT:
            files.extend(glob.glob(directory + "*" + extension))

    # Get details of files
    files_with_mtime = []
    for file in files:
        file_date = get_date_from_file(file)
        files_with_mtime.append(
            (file, file_date.strftime("%m_%B"), file_date.strftime("%Y") )
        )
    return files_with_mtime

def create_directories(dir_names, parent_dir=""):
    """ create directories for names passed in """
    for i in set(dir_names):
        try:
            new_dir = os.path.join(TARGET, parent_dir, i)
            if not os.path.exists(new_dir):
                print("+>\t", new_dir)
                os.makedirs(os.path.join(TARGET, parent_dir, i))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

def create_directories_for_files(files):
    """ creates month and year directories for a list of files """
    # Loop over months to create a month list
    month_list = []
    for i in files:
        month_list.append(i[1])
    # Loop over years to create a year list
    year_list = []
    for i in files:
        year_list.append(i[2])
    # Convert to sets
    year_set = set(year_list)
    month_set = set(month_list)

    print("\nCreating New Directories")
    # Create year directories
    create_directories(year_set)
    # loop year_set to create month sub directories
    for year in year_set:
        create_directories(month_set, year)

def confirm_overwrite_file(old_file, new_file):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    print("\nDuplicate filename found at:\n\t", new_file)
    print("For file:\n\t", old_file)
    choice = input("Overwrite file? [Y/n] > ").lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")

def move_files_to_folders(files):
    """ gets tuple(file, month, year) from create_file_list() then moves the files """
    action = "Moving" if ARGS.move else "Copying"
    print("\n", action, "files to new structure!\n")
    files_moved = 0
    for i in files:
        try:
            filename = os.path.basename(i[0])
            old_path = os.path.join(i[0])
            new_path = os.path.join(TARGET, (i[2] + '/' + i[1] + '/' + filename))
            print(os.path.exists(new_path))
            # Overwrite file check
            if (
                not os.path.exists(new_path)
                or ARGS.overwrite
                or confirm_overwrite_file(old_path, new_path)
            ):
                if ARGS.move:
                    print("\nMoving:", old_path)
                    shutil.move(old_path, new_path)
                else:
                    print("\nCopying:", old_path)
                    shutil.copy2(old_path, new_path)
                print("To:", new_path)
                files_moved += 1
        except Exception:
            raise
    return files_moved


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(prog=sys.argv[0], usage='%(prog)s [options]')
    PARSER.add_argument("directory", help="Directory to gather files from")
    PARSER.add_argument("extension", help="File extensions to match")
    PARSER.add_argument("-t", "--target", help="Directory to output to", default=os.getcwd())
    PARSER.add_argument("-m", "--move", help="Move files instead of copying them", default=False)
    PARSER.add_argument("-o", "--overwrite", help="Overwrite existing files", default=False)
    ARGS = PARSER.parse_args()
    print("Moving files in a Year/Month structure")
    TARGET = os.path.abspath(ARGS.target)
    print("\nTo:\n=>\t", TARGET)
    EXT = ['.' + e for e in str.split(ARGS.extension)]
    print("\nWith extensions:", EXT)
    DIRS = glob.glob(os.path.abspath(ARGS.directory) + "/")
    print("\nInside directories:")
    for globbed_dir in DIRS:
        print('->\t', globbed_dir)
    FILES = create_file_list(DIRS)
    create_directories_for_files(FILES)
    print("Moved %i files" % move_files_to_folders(FILES))
