import os
import ycm_core


# -----------------------------------------------------------------------------
# Utilities

def dir_of_this_script():
    return os.path.dirname(os.path.abspath(__file__))


def basename_of_this_script():
    return os.path.basename(__file__)


def is_header_file(filename):
    extension = os.path.splitext(filename)[1]
    return extension in HEADER_EXTENSIONS


def apply_flag(flag, parameters, combine):
    applied = []

    for parameter in parameters:
        if combine:
            applied.append(flag + parameter)
        else:
            applied.append(flag)
            applied.append(parameter)

    return applied


def match_pattern(patterns, string, case_sensitive):
    if not patterns:
        return False

    if case_sensitive:
        actual_patterns = patterns
    else:
        actual_patterns = []
        for pattern in patterns:
            actual_patterns.append(pattern.lower())

    return string.lower() in actual_patterns


def match_path_basename(patterns, path, case_sensitive):
    name = os.path.basename(path)
    return match_pattern(patterns, name, case_sensitive)


def find_matched_dirs(patterns, top, case_sensitive):
    matched = set()

    for root, dirs, files in os.walk(top):
        if match_path_basename(patterns, root, case_sensitive):
            matched.add(root)

    return matched


def find_dirs_contain_files(patterns, top, case_sensitive):
    matched = set()

    for root, dirs, files in os.walk(top):
        for f in files:
            ext = os.path.splitext(f)[1]
            if match_pattern(patterns, ext, case_sensitive):
                matched.add(root)
                break

    return matched


def union_dir(dirs, others):
    for other in others:
        should_add = True

        for current in dirs:
            if other.startswith(current):
                should_add = False
                break

        if should_add:
            dirs.add(other)


def find_header_dirs(top, case_sensitive):
    dirs = set()

    dirs = find_matched_dirs(HEADER_DIRS, top, case_sensitive)
    others = find_dirs_contain_files(HEADER_EXTENSIONS, top, case_sensitive)
    union_dir(dirs, others)

    return dirs


def make_user_header_flags(top, header_dirs):
    if os.path.isabs(top):
        dirs = find_header_dirs(top, False)
    else:
        dirs = find_header_dirs(os.path.join(THIS_CONF_DIR, top), False)

    dirs.difference_update(header_dirs)
    header_flags = apply_flag('-I', dirs, True)

    return header_flags, dirs


def add_user_header_flags(top, flags, header_dirs):
    header_flags, dirs = make_user_header_flags(top, header_dirs)
    flags.extend(header_flags)
    header_dirs.update(dirs)


def get_compilation_info_for_file(filename):
    if is_header_file(filename):
        basename = os.path.splitext(filename)[0]
        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension
            if os.path.exists(replacement_file):
                compilation_info = database.GetCompilationInfoForFile(
                    replacement_file)
                if compilation_info.compiler_flags_:
                    return compilation_info
        return None
    return database.GetCompilationInfoForFile(filename)


# -----------------------------------------------------------------------------
# Common settings

SYSTEM_NAME = os.uname()[0]
SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']
HEADER_EXTENSIONS = ['.h', '.hxx', '.hpp', '.hh']
HEADER_DIRS = ['include', 'inc', 'headers']
THIS_CONF_BASENAME = basename_of_this_script()
THIS_CONF_DIR = dir_of_this_script()


# -----------------------------------------------------------------------------
# Compilation database settings

# By adding
# set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# to generate compilation databse (compile_commands.json)

compilation_database_folder = ''

if os.path.exists(compilation_database_folder):
    database = ycm_core.CompilationDatabase(compilation_database_folder)
else:
    database = None


# -----------------------------------------------------------------------------
# Manual settings

manual_header_dirs = set()

# Base flags
manual_flags = [
    '-Wall',
    '-Wextra',
    '-Werror',
    '-Wno-long-long',
    '-Wno-variadic-macros',
    '-fexceptions',
    '-DNDEBUG',
    '-std=c++14',
    '-xc++',
]

# System header dirs
if SYSTEM_NAME == 'Darwin':
    system_header_dirs = {
        '/usr/local/opt/openssl/include',
        '/usr/local/opt/qt/include',
        '/usr/local/opt/icu4c/include',
        '/usr/local/include/gtk-3.0',
        '/usr/local/include/gtkmm-3.0',
        '/usr/local/Frameworks/Python.framework/Versions/3.6/Headers'
    }

    system_header_flags = apply_flag('-isystem', system_header_dirs, False)
elif SYSTEM_NAME == 'Linux':
    system_header_dirs = {
        '/usr/include/c++/5',
        '/usr/local/include',
        '/usr/include',
    }

    system_header_flags = apply_flag('-I', system_header_dirs, True)
else:
    system_header_dirs = set()
    system_header_flags = []

manual_header_dirs.update(system_header_dirs)
manual_flags.extend(system_header_flags)

# User header dirs
add_user_header_flags(THIS_CONF_DIR, manual_flags, manual_header_dirs)


# -----------------------------------------------------------------------------
# Main callback
def FlagsForFile(filename, **kwargs):
    if not database:
        return {
            'flags': manual_flags,
            'include_paths_relative_to_dir': THIS_CONF_DIR
        }

    compilation_info = get_compilation_info_for_file(filename)
    if not compilation_info:
        return None

    compilation_info_flags = list(compilation_info.compiler_flags_)

    return {
        'flags': compilation_info_flags,
        'include_paths_relative_to_dir': compilation_info.compiler_working_dir_
    }
