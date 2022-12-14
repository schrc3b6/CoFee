from __future__ import annotations
from enum import Enum, auto
import os
import re
import sys
from typing import List
import cofee.settings as settings
from cofee.hint import Hint,HintAction
from cofee.types import HintAction,ErrorResult,ErrorType
from cofee.location import Location
from string import Template

class ErrorMessages:

    def __init__(
            self,
            msg: str="",
            locations: List[Location] = None
        ):
        self.msg = msg
        if locations is None:
            locations=[]
        self.locations=locations
        self.nr=-1

    def append_src(self, error_src, can_fail=False):
        if os.path.isabs(error_src.filename):
            path=os.path.relpath(error_src.filename,start=settings.project_dir)
        else:
            if settings.srcdir:
                path=settings.srcdir+'/'+error_src.filename
            else:
                path=error_src.filename
        if os.path.exists(path):
            error_src.filename= path
            error_src.save_codelines()
            if len(error_src.codelines) > 2:
                self.locations.append(error_src)
        else:
            if can_fail:
                self.locations.append(error_src)
            else:
                print(
                    "Could not open file for Error Source handling: " +
                    path,
                    file=sys.stderr)

class Error:

    def __init__(
            self,
            title: str|None = None,
            error_type: ErrorType|None = ErrorType.ERROR,
            kind: ErrorResult = ErrorResult.ERROR,
            category: str = "",
            tool: str = "",
            hint: Hint|None = None,
            msgs: List[ErrorMessages] = None,
            artefacts: List[str] = None,
            extra_vars= None,
            raw: str|None = None 
            ):
        self.__title = title
        self.type = error_type
        self.kind = kind
        self.category = category
        self.tool = tool
        self.hint = hint
        if msgs is None:
            msgs=[]
        self.msgs = msgs
        if artefacts is None:
            artefacts=[]
        self.artefacts = artefacts
        if extra_vars is None:
            extra_vars= dict()
        self.extra_vars = extra_vars
        self.raw = raw
        self.nr=-1

    @property
    def title(self) -> str:
        if self.__title == None:
            if self.type == ErrorType.UNITTEST:
                return "Unit-Test: " + str(self.kind.name) + " - " + self.category
            else:
                return str(self.kind.name) + " - " + self.category

        else:
            return self.__title

    @title.setter
    def title(self, title: str|None):
        self.__title = title

    # def append_error_msg(self, value: str):
    #     if self.msg is not None:
    #         self.msg = self.msg + value
    #     else:
    #         self.msg = value
    #
    # def prepend_error_msg(self, value: str):
    #     if self.msg is not None:
    #         self.msg = value + self.msg
    #     else:
    #         self.msg = value
    def extend_hint(self):
        if self.hint is None:
            return
        self.hint.msg= Template(self.hint.msg).safe_substitute(self.extra_vars)
        return

    def generate_error_msg(self):
        string=""
        if self.hint:
            if self.hint.action == HintAction.DELETE:
                return ""
            if self.hint.action== HintAction.REPLACEWITHMESSAGE:
                for msg in self.msgs:
                    string= string + msg.msg + "\n\n"
                return string + self.hint.as_text
            if self.hint.action== HintAction.REPLACE or self.hint.action == HintAction.REPLACEALL:
                return self.hint.as_text
            if self.hint.action == HintAction.PREPEND:
                string= string + self.hint.as_text + "\n\n"    
        string=string + str(self.kind.name)+": " 
        for msg in self.msgs:
            string= string + msg.msg + "\n\n"
            for idx, source in enumerate(msg.locations):
                if source.filename is not None:
                    string += str(source)
                    if idx < len(msg.locations) - 1:
                        string += '\nwas called by:\n'
            # string= string + "\n\n"
        if self.hint:
            if self.hint.action == HintAction.APPEND:
                string = string +"\n" + self.hint.as_text    
        return string

    def __str__(self):
        if self.msgs:
            return self.generate_error_msg()
        else:
            return "ERROR without error Message encountered"


    def print_error(self):
        print("Printing the error:")
        print("Errortitle: " + self.title)
        if self.type is not None:
            print("Errortype: " + self.type.name)
        if self.tool is not None:
            print("Tool: " + self.tool)
        if self.kind is not None:
            print("Errorkind: " + self.kind.name)
        if self.category is not None:
            print("Errorcategory: " + self.category)
        for idx,msg in enumerate(self.msgs):
            print("Message" + str(idx) + ": " + msg.msg)
            for source in msg.locations:
                if source.filename is not None:
                    print("Sourcefile: " + source.filename)
                if source.linenumber is not None:
                    print("Linenumber: ", source.linenumber_editor)
                if source.column is not None:
                    print("Column: ", source.column)
                if source.start_column is not None:
                    print("Start-Column: ", source.start_column)
                if source.finish_column is not None:
                    print("Finish-Column: ", source.finish_column)
        print("##############################")

