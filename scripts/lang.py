from genericpath import isfile
from io import TextIOWrapper
from os import getcwd, listdir, path
from os.path import isfile, join
import json
import re


# git diff 1.20.x 14f1850  -- ./Xplat/src/main/resources/assets/botania/lang/en_us.json > en_us.diff


cwd = getcwd()
LANG_PATH = path.join("Xplat", "src", "main", "resources", "assets", "botania", "lang")
LANG_PATH = path.join(cwd, LANG_PATH)

FIRST_LINE = "### STATUS"
SECOND_LINE = "| lang | count | extra | missing |"
THIRD_LINE = "| :--: | :--: | :--: | :--: |"

EN_US = "en_us"

COMMENT = "_comment"
NO_VALUE = ""
NOTHING = "( NOTHING )"

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
        return f"| {self.lang} | {self.count} | {self.extra} | {self.missing} | "


def count_sort(element:LangMeta):
    return element.count


def get_list_lang_id()->list[str]:
    list_lang_id = [f.split(".")[0] for f in listdir(LANG_PATH) if isfile(join(LANG_PATH, f))]
    list_lang_id.remove(EN_US)
    return list_lang_id


def get_json_dict(filepath)-> dict: 
    return json.load(filepath)


def is_not_comment(text:str):
    return COMMENT_REGEX.search(text) is None


def get_lang_dict(lang_id:str)-> dict[str, str]:
    lang_dict = {}
    lang_file_path = path.join(LANG_PATH, f"{lang_id}.json")
    with open(lang_file_path, mode="r", encoding="utf-8") as lang_file:
        lang_json = get_json_dict(lang_file)
        for key in lang_json.keys():
            if is_not_comment(key):
                lang_dict[key] = NO_VALUE
    return lang_dict


def subtract_dict(dict_a, dict_b):
    return {k:v for k,v in dict_a.items() if k not in dict_b}


def compare_lang(lang_alt:str, lang_main:str=EN_US, print_as_md:bool=True):
    dict_main = get_lang_dict(lang_main)
    dict_alt = get_lang_dict(lang_alt)
    dict_missing = subtract_dict(dict_main, dict_alt)
    dict_extra = subtract_dict(dict_alt, dict_main)
    if print_as_md:
        print(" ")
        print_dict_missing(dict_missing, lang_main, lang_alt)
        print(" ")
        print_dict_extra(dict_extra, lang_main, lang_alt)
        print(" ")
    return LangMeta(lang_alt, len(dict_alt), len(dict_extra), len(dict_missing))


def print_dict_missing(dict_missing, lang_main, lang_alt):
    print(f"### PRESENT IN (`{lang_main}`) BUT MISSING FROM (`{lang_alt}`)")
    if len(dict_missing) == 0:
        print(NOTHING, end="<br>\n")
    else:
        for element in dict_missing:
            print(f"`{element}`", end="<br>\n")


def print_dict_extra(dict_extra, lang_main, lang_alt):
    print(f"### PRESENT IN (`{lang_alt}`) BUT MISSING FROM (`{lang_main}`)")
    if len(dict_extra) == 0:
        print(NOTHING, end="<br>\n")
    else:
        for element in dict_extra:
            print(element, end="<br>\n")


def get_todo_line(line:str):
    return TODO_REGEX.sub(TODO_VALUE, line)


def clone_file(lang_id:str):
    lang_file_path = path.join(LANG_PATH, f"{lang_id}.json")
    original_lang_file_path = path.join(LANG_PATH, "en_us.json")
    with open(original_lang_file_path, mode="r", encoding="utf-8") as original_file:
        with open(lang_file_path, mode="w", encoding="utf-8") as lang_file:
            for original_line in original_file:
                handle_original_line(original_line, lang_file)


def handle_original_line(original_line:str, lang_file:TextIOWrapper):
    if is_not_comment(original_line):
        todo_line = get_todo_line(original_line)
        lang_file.write(todo_line)
    else:
        lang_file.write(original_line)


def get_list_lang_meta()->list[LangMeta]:
    list_lang_meta = create_list_lang_meta()
    list_lang_id = get_list_lang_id()
    add_alt_lang_meta(list_lang_meta, list_lang_id)
    sort_list_lang_meta(list_lang_meta)
    add_main_lang_meta(list_lang_meta)
    return list_lang_meta


def add_alt_lang_meta(list_lang_meta:list[LangMeta], list_lang_id:list[str]):
    for lang_id in list_lang_id:
        lang_meta = compare_lang(lang_id, print_as_md=False)
        list_lang_meta.append(lang_meta)


def sort_list_lang_meta(list_lang_meta:list[LangMeta]):
    list_lang_meta.sort(key=count_sort, reverse=True)


def add_main_lang_meta(list_lang_meta:list[LangMeta]):
    list_lang_meta.sort(key=count_sort, reverse=True)
    lang_meta = compare_lang(EN_US, print_as_md=False)
    list_lang_meta.insert(0, lang_meta)
    

def create_list_lang_meta()->list[LangMeta]:
    return []


def get_translation_status() -> None:
    list_lang_meta = get_list_lang_meta()
    print(FIRST_LINE)
    print(SECOND_LINE)
    print(THIRD_LINE)
    for lang_meta in list_lang_meta:
        print(lang_meta)
    print(" ")


if __name__ == "__main__":
    get_translation_status()
    compare_lang("fr_fr")
    # clone_file("lol_us")
