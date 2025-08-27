import re
def check_path_validity(path_string):
    path_regex = re.compile(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$')
    return bool(path_regex.match(path_string))