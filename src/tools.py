from pandas import read_csv, DataFrame
import os.path
import re

try:
    from IPython.display import clear_output
except Exception:
    pass

def load_csv(filepath, columns):
    if os.path.exists(filepath):
        return read_csv(filepath)
    else:
        return DataFrame(columns=columns)

def load_data(filepath, columns, method="csv"):
    if method == 'csv':
        return load_csv(filepath, columns)

def store_data(df, filepath, columns, method="csv"):
    if method == 'csv':
        store_csv(filepath, df[columns])

def store_csv(filepath, df):
    dir_name = '/'.join(filepath.split('/')[:-1])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("Directory " , dir_name ,  " Created ")
    df.to_csv(filepath)
    print(f'{filepath} Created')

def strip_list(string_list, replace="", to=""):
    if replace and len(replace)> 0:
        string_list = [re.sub(replace, to, x) for x in string_list]
    string_list = [x.strip() for x in string_list]
    return string_list

def store_data(df, filepath, columns, method="csv"):
    if method == 'csv':
        store_csv(filepath, df[columns])

def latin_to_utf8(word):
    return word.encode('latin-1').decode('utf-8', 'ignore')

def print_progress(current=1, total=1, title=None, current_file=None):
    """
        Desc: Print Progress on Console
        Params:
            - current: int(current position)
            - total: int(final position)
            - title: str(title of process)
            - current_file: str(displays current_file name)
        Returns: None
    """
    if total == 0:
        return
    progress = current/total * 100
    load_bar = '|'*int(progress/2) + '.'*int((total-current)/total*100/2)
    clear_output(wait=True)
    output = f'Loading {title}: {load_bar} {round(progress, 1)}%'
    output += f' (current: {current_file})' if current_file else ''
    print(output)
