import itertools
import random
from decimal import Decimal


def get_random_str(size: int = 10):
    ret = []
    for i in range(0, size):
        ret.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    return "delete_" + "".join(ret)


indent = "   "


def print_with_newline(self, cur_indent):
    self_dict = self.__dict__
    name = self.__class__.__name__
    keys = list(self.__annotations__.keys())
    next_indent = cur_indent + indent
    ret = f"{cur_indent}{name}:\n"
    for key in keys:
        val = self_dict.get(key, "undefined")
        if isinstance(val, list):
            ret += f"{next_indent}{key}=[\n"
            for v in val:
                if hasattr(v, "__dict__"):
                    ret += f"{str(print_with_newline(v, next_indent + indent))}\n"
                else:
                    ret += f"{next_indent + indent}{str(v)}\n"
            ret += f"{next_indent}]\n"
        else:
            ret += next_indent + key + "=" + str(val) + "\n"
    return ret


def flatten_list(param: list):
    return list(itertools.chain.from_iterable(param))


def extract_str(from_str, start_keyword, end_keyword=None, include_keyword=False, find_from_right=False):
    start_offset = 0 if include_keyword else len(start_keyword)
    before_start_removed = from_str[from_str.find(start_keyword) + start_offset :]
    if end_keyword:
        end_offset = len(end_keyword) if include_keyword else 0
        if find_from_right:
            return before_start_removed[: before_start_removed.rfind(end_keyword) + end_offset]
        else:
            return before_start_removed[: before_start_removed.find(end_keyword) + end_offset]
    else:
        return before_start_removed


def get_decimal(num, divider=10000):
    return Decimal(num * divider) / divider
