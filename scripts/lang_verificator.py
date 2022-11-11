from genericpath import isfile
from os import getcwd, listdir, path
from os.path import isfile, join
import json
import re


cwd = getcwd()
LANG_PATH = path.join("Xplat", "src", "main", "resources", "assets", "botania", "lang")
LANG_PATH = path.join(cwd, LANG_PATH)


COMMENT = "_comment"
NOTHING = ""

TODO_VALUE = '": "TODO: '
TODO_PATTERN = r'"( )*:( )*"'
TODO_REGEX = re.compile(TODO_PATTERN)

COMMENT_PATTERN = "_comment"
COMMENT_REGEX = re.compile(COMMENT_PATTERN)


class LangMeta():
    def __init__(self, lang:str, count:int, extra_lines:int, missing_lines:int):
        self.lang = lang
        self.count = count
        self.extra = extra_lines
        self.missing = missing_lines
    def __str__(self) -> str:
        return f"| {self.lang} | {self.count} | {self.missing} | {self.extra} | "


def count_sort(element:LangMeta):
    return element.count


def get_lang_files():
    lang_files = [f.split(".")[0] for f in listdir(LANG_PATH) if isfile(join(LANG_PATH, f))]
    lang_files.remove("en_us")
    return lang_files


def get_json_dict(filepath)-> dict: 
    return json.load(filepath)


def is_not_comment(text:str):
    return COMMENT_REGEX.search(text) is None


def get_lang_dict(lang_id:str):
    lang_dict = {}
    lang_file_path = path.join(LANG_PATH, f"{lang_id}.json")
    with open(lang_file_path, mode="r", encoding="utf-8") as lang_file:
        lang_json = get_json_dict(lang_file)
        for key in lang_json.keys():
            if is_not_comment(key):
                lang_dict[key] = NOTHING
    return lang_dict


def subtract_dict(dict_a, dict_b):
    return {k:v for k,v in dict_a.items() if k not in dict_b}


def compare_lang(lang_alt:str, lang_main:str="en_us", is_md:bool=False):

    dict_main = get_lang_dict(lang_main)
    dict_alt = get_lang_dict(lang_alt)

    dict_extra = subtract_dict(dict_main, dict_alt)
    dict_missing = subtract_dict(dict_alt, dict_main)

    if is_md:
        print(" ")
        print(f"### PRESENT IN (`{lang_main}`) BUT ABSENT FROM (`{lang_alt}`)")
        for element in dict_extra:
            print(element, end="<br>\n")
        print(" ")
        print(f"### PRESENT IN (`{lang_alt}`) BUT ABSENT FROM (`{lang_main}`)")
        for element in dict_missing:
            print(element, end="<br>\n")
        print(" ")

    return LangMeta(lang_alt, len(dict_alt), len(dict_extra), len(dict_missing))


def get_todo_line(line:str):
    return TODO_REGEX.sub(TODO_VALUE, line)


def clone_file(lang_id:str):
    lang_file_path = path.join(LANG_PATH, f"{lang_id}.json")
    original_lang_file_path = path.join(LANG_PATH, "en_us.json")

    with open(original_lang_file_path, mode="r", encoding="utf-8") as original_file:
        with open(lang_file_path, mode="w", encoding="utf-8") as lang_file:
            for original_line in original_file:

                if is_not_comment(original_line):
                    todo_line = get_todo_line(original_line)
                    lang_file.write(todo_line)
                else:
                    lang_file.write(original_line)


def get_lang_list()->list[LangMeta]:
    lang_files = get_lang_files()
    lang_list = []

    for lang_file in lang_files:
        lang_meta = compare_lang(lang_file)
        lang_list.append(lang_meta)
    
    lang_list.sort(key=count_sort, reverse=True)
    lang_meta = compare_lang("en_us")
    lang_list.insert(0, lang_meta)
    return lang_list


def get_translation_status():
    lang_list = get_lang_list()
    for lang in lang_list:
        print(lang)
    print(" ")


if __name__ == "__main__":
    get_translation_status()
    # compare_lang("ja_jp", is_md=True)
    # clone_file("lol_us")
