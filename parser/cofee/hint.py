from __future__ import annotations
from cofee.types import ErrorType,HintAction


class Hint:

    def __init__(
            self,
            tool: str|None = None,
            category: str|None = None,
            action: str|None = None,
            msg: str|None = None,
            unit_test_src: str|None = None,
            start_line: int|None = None,
            end_line: int|None = None
        ):
        self.category = category
        self.tool = tool
        self.unit_test_src = unit_test_src
        if action:
            if action in ("replace", "Replace", "REPLACE"):
                action=HintAction.REPLACE
            if action in ("replaceall", "Replaceall", "ReplaceAll", "REPLACEALL"):
                action=HintAction.REPLACEALL
            if action in ("replaceWithMessage", "REPLACEWITHMESSAGE", "replacewithmessage"):
                action=HintAction.REPLACEWITHMESSAGE
            if action in ("prepend", "Prepend", "PREPEND"):
                action=HintAction.PREPEND
            if action in ("append", "Append", "APPEND"):
                action=HintAction.APPEND
            if action in ("delete", "Delete", "DELETE"):
                action=HintAction.DELETE

        self.action = action
        self.msg = msg
        self.start_line = start_line
        self.end_line = end_line

    @property
    def as_text(self):
        if self.unit_test_src == None:
            return self.msg
        else:
            return self.msg + "\nFür den Test wurde der folgende Code ausgeführt:\n" + self.unit_test_src
        
    def __hash__(self):
        return hash(self.category)

    def __eq__(self, other):
        return self.tool == other.tool and self.category == other.category

    def __str__(self):
        if (self.tool is not None and self.category is not None and
            self.action is not None and self.msg is not None):
            return self.tool + " " + self.category + \
                " " + self.action.name + " " + self.msg
        return ""


class HintManager:

    def __init__(self):
        self.__hints = set()

    def add_hint(self, hint: Hint):
        self.__hints.add(hint)

    def __iter__(self):
        return self.__hints.__iter__()

    def merge(self, hm):
        for hint in hm:
            self.add_hint(hint)

    def __len__(self):
        return self.__hints.__len__()

    def get_hint(self, tool, category):
        # if " " in category:
        #     category=category.replace(" ","-")
        for hint in self.__hints:
            if hint.tool == tool and hint.category == category:
                return hint
        return None

