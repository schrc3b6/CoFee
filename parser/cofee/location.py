from __future__ import annotations
import os

class Location:
    """
    Location = {
        "filename": filename,
        "linenumber": linenumber,
        "column": column
    }
    """

    def __init__(
            self,
            filename: str|None = None,
            linenumber: int|None = None,
            column: int|None = None,
            start_column: int|None = None,
            finish_column: int|None = None,
            file_info: bool = True): # what is file_info!!!
        self.filename = filename
        self.linenumber = linenumber
        self.column = column
        self.start_column = start_column
        self.finish_column = finish_column
        self.file_info = file_info
        self.nr=-1
        self.codelines=''

    @property
    def srccode(self):
        string=''.join(self.codelines)
        if string[-1:] == '\n':
            return string[:-1]
        return string

    @property
    def linenumber_editor(self):
        return self.linenumber+1

    @property
    def basename(self):
        return os.path.basename(self.filename)

    def save_codelines(self):
        error_lines = []
        if self.filename is not None and self.linenumber is not None:
            with open(self.filename, 'r') as EF:
                code_lines = EF.readlines()
                if len(code_lines) < 1:
                    self.codelines = []
                    return
                error_lines.append(
                    code_lines[self.linenumber].replace('\t', ' '))
                if self.linenumber > 1:
                    error_lines.insert(
                        0, code_lines[self.linenumber - 1].replace('\t', ' '))
                else:
                    error_lines.insert(0, ' ')
                if self.linenumber < len(code_lines) - 1:
                    error_lines.append(
                        code_lines[self.linenumber + 1].replace('\t', ' '))
                else:
                    error_lines.append(' ')
        self.codelines = error_lines

    # def get_codelines(self):
    #     error_lines = []
    #     if self.filename is not None and self.linenumber is not None:
    #         with open(self.filename, 'r') as EF:
    #             code_lines = EF.readlines()
    #             error_lines.append(
    #                 code_lines[self.linenumber].replace('\t', ' '))
    #             if self.linenumber > 1:
    #                 error_lines.insert(
    #                     0, code_lines[self.linenumber - 1].replace('\t', ' '))
    #             else:
    #                 error_lines.insert(0, ' ')
    #             if self.linenumber < len(code_lines) - 1:
    #                 error_lines.append(
    #                     code_lines[self.linenumber + 1].replace('\t', ' '))
    #             else:
    #                 error_lines.append(' ')
    #     return error_lines

    def generateMark(self, error_lines):
        # set a '^'-caret if possible
        string = ''
        if self.column is not None:
            # set underline before and after caret
            if self.start_column is not None and self.finish_column is not None:
                caret = ' ' * self.start_column + '~' * \
                    (self.column - self.start_column) + '^'
                string += caret + '~' * \
                    (self.finish_column - self.column) + '\n'
            # set underline just before caret
            elif self.start_column is not None:
                string += ' ' * self.start_column + '~' * \
                    (self.column - self.start_column) + '^'
            # set underline just after caret
            elif self.finish_column is not None:
                caret = '^'.rjust(self.column)
                string += caret + '~' * \
                    (self.finish_column - self.column) + '\n'
            # set underline without knowing the endpoint
            else:
                caret = '^'.rjust(self.column)
                string += caret + '~' * \
                    (len(error_lines[1]) - self.column - 1) + '\n'
        # set underline that is not defined through the analyze
        else:
            idx2 = 0
            for idx2, elem in enumerate(error_lines[1]):
                # iterate until first non-space-char
                if not elem.isspace():
                    break
            # print same amount of whitespaces like the line before and
            # underlines in the same amount like the length of the line before
            string += ' ' * idx2 + '~' * \
                (len(error_lines[1]) - idx2 - 1) + '\n'
        return string

    def __str__(self):
        string = ''
        if self.filename is not None:
            if self.file_info:
                string += 'File: ' + self.filename
            if self.linenumber is not None:
                if self.file_info:
                    string += ' line ' + str(self.linenumber_editor) + ':\n\n'
                else:
                    string += 'Error located here: \n\n'
                # insert sourcecode-lines
                error_lines = self.codelines
                string += error_lines[0]
                string += error_lines[1]
                string += self.generateMark(error_lines)
                string += error_lines[2]
        return string

