from __future__ import annotations
import os
import plistlib
import re
import json
import sys
import glob
from lxml import etree as ET
from cofee.location import Location
from cofee.error import Error, ErrorType, ErrorMessages, ErrorResult
import cofee.settings as settings

class Parser:

    @staticmethod
    def parse(input_file: str):
        extension = os.path.splitext(input_file)
        if extension[1] == '.plist':
            return PlistParser.parse(input_file)
        if extension[1] == '.make':
            return MakeParser.parse(input_file)
        if extension[1] == '.tidy':
            return TidyParser.parse(input_file)
        if extension[1] == '.valgrind':
            return ValgrindParser.parse(input_file)
        if extension[1] == '.cmocka':
            return CMockaParser.parse(input_file)
        if extension[1] == '.makecm':
            return MakeParser.parse(input_file, category="MakeCmocka", tool="makecmocka")
        if extension[1] == '.asan':
            return SanitizerParser.parse(input_file)
        if extension[1] == '.tsan':
            return SanitizerParser.parse(input_file)
        if extension[1] == '.msan':
            return SanitizerParser.parse(input_file)
        if os.path.splitext(extension[0])[1] == ".msan":
            return SanitizerParser.parse(input_file)
        if os.path.splitext(extension[0])[1] == ".asan":
            return SanitizerParser.parse(input_file)
        if os.path.splitext(extension[0])[1] == ".tsan":
            return SanitizerParser.parse(input_file)
            # return SimpleParser.parse(input_file,"thread","Sanatyzer")

        # No Parser for that file type
        return []

class PlistParser:

    @staticmethod
    def parse(input_file: str):
        errors = []
        with open(input_file, 'rb') as IF:
            test_case = plistlib.load(IF)
            diagnostics = test_case['diagnostics']
            for diag in diagnostics:
                # For scan-build category 'type' 
                error = Error(
                    category=diag.get('description'),
                    tool='static-analyzer')
                # error_func = diag.get("issue_context")
                msg=ErrorMessages(diag.get('description'))
                location = diag.get('location')
                file_names = test_case['files']
                source = Location(filename=file_names[location.get(
                    'file')], linenumber=location.get('line') - 1, column=location.get('col'))
                msg.append_src(source)
                error.msgs.append(msg)
                report_path=input_file+'.html'
                if os.path.exists(report_path):
                    x=settings.pages_url.find('.de')
                    hash=diag.get('issue_hash_content_of_line_in_context')
                    if hash:
                        url=settings.pages_url[0:x+4]+'-'+settings.pages_url[x+3:] +'/-/jobs/' + settings.job_id + '/artifacts/' + report_path + '#reportHash=' + hash 
                    else:
                        url=settings.pages_url[0:x+4]+'-'+settings.pages_url[x+3:] +'/-/jobs/' + settings.job_id + '/artifacts/' + report_path
                    error.artefacts.append(url)
                errors.append(error)
        # report_path=os.path.dirname(input_file)
        # print("REPORT-PATH:"+report_path)
        # if os.path.exists(report_path+'/index.html'):
        #     x=settings.pages_url.find('.de')
        #     url=settings.pages_url[0:x+4]+'-'+settings.pages_url[x+3:] +'/-/jobs/' + settings.job_id + '/artifacts/' + report_path + '/index.html'
        #     for error in errors:
        #         error.artefacts.append(url)
        return errors


class MakeParser:

    @staticmethod
    def parse(input_file: str, category: str = "Makefile", tool: str = "makefile"):
        errors = []
        msg_lines = ""
        with open(input_file, 'rb') as IF:
            # iterate through input_file if multiple .json-dicts are in the
            # same .make-file
            for line in IF:
                try:
                    test_cases = json.loads(line)
                    # exit-condition if output is empty
                    if bool(test_cases):
                        for test_case in test_cases:
                            if test_case['kind'] in ( 'note', 'Note'):
                                #TODO
                                continue;
                            error = Error(
                                category="Compile Error",
                                tool=tool)
                            if test_case['kind'] in ( 'Warning', 'warning'):
                                error.kind=ErrorResult.WARNING
                            if "option" in test_case:
                                error.category=test_case['option'][2:]
                            msg=ErrorMessages(test_case['message'])
                            locations = test_case['locations']
                            for location in locations:
                                caret_location = location['caret']
                                source = Location(
                                    filename=caret_location['file'],
                                    linenumber=caret_location['line'] - 1,
                                    column=caret_location['column'])
                                # set start and endpoint of underline if
                                # possible
                                if 'start' in location:
                                    start_location = location['start']
                                    source.start_column = start_location['column']
                                if 'finish' in location:
                                    finish_location = location['finish']
                                    source.finish_column = finish_location['column']
                                msg.append_src(source)
                            error.msgs.append(msg)
                            errors.append(error)
                    else:
                        # go next
                        pass
                except ValueError:
                    # exit-condition if output is empty
                    if len(line) < 1:
                        continue
                    else:
                        msg_lines = msg_lines + line.decode("utf-8")
        # parse not json lines
        parsed_txt=False
        
        if len(msg_lines) != 0:
            if (match := re.search(r"No rule to make target '(?P<file>[^']+)'", msg_lines)) is not None:
                error = Error(
                    category='Makefile File not Found',
                    msgs=[ErrorMessages(msg_lines)],
                    tool=tool,
                    raw=msg_lines,
                    extra_vars={"file": match.group('file')}
                )
                errors.append(error)
                parsed_txt=True
            elif (match := re.search(r"no makefile found", msg_lines)) is not None:
                error = Error(
                    category='No Makefile',
                    msgs=[ErrorMessages(msg_lines)],
                    tool=tool,
                    raw=msg_lines
                )
                errors.append(error)
                parsed_txt=True
            else:
            ## match any of these
                for match in re.finditer(r"undefined reference to `(?P<func>[^']+)'", msg_lines):
                    error = Error(
                        category='Makefile Missing Function',
                        msgs=[ErrorMessages("Undefined reference to {}".format(match.group('func')))],
                        tool=tool,
                        raw=msg_lines,
                        extra_vars={"func": match.group('func')}
                    )
                    errors.append(error)
                    parsed_txt=True
                for match in re.finditer(r"multiple definition of `(?P<func>[^']+)'", msg_lines):
                    error = Error(
                        category='Makefile Function Multiple Implementations',
                        msgs=[ErrorMessages("Multiple definitions of {}".format(match.group('func')))],
                        tool=tool,
                        raw=msg_lines,
                        extra_vars={"func": match.group('func')}
                    )
                    errors.append(error)
                    parsed_txt=True

            if not parsed_txt: 
                error = Error(
                    category=category,
                    msgs=[ErrorMessages(msg_lines)],
                    tool=tool,
                    raw=msg_lines
                )
                errors.append(error)
        return errors


class SimpleParser:

    @staticmethod
    def parse(input_file: str, category: str, tool: str):
        errors = []
        # exit-condition if output is empty
        with open(input_file, 'r') as IF:
            orig_msg = IF.read()
        if len(orig_msg) >= 12:
            error = Error(
                category=category,
                msgs=[ErrorMessages(orig_msg)],
                tool=tool,
                raw=orig_msg    
            )
            errors.append(error)
        return errors


class TidyParser:
    checks=r"\[misc-definitions-in-headers\]|\[bugprone-suspicious-include\]"

    @staticmethod
    def parse(input_file: str):
        errors = []
        regex = re.compile(TidyParser.checks,0)
        with open(input_file, 'r') as IF:
            orig_msg = IF.readlines()
            for line in orig_msg:
                match = regex.search(line)
                if match is not None:
                    test_case = line.split(':')
                    error = Error(
                        category=match.group()[1:-1],
                        tool='clang-tidy')
                    msg=ErrorMessages(test_case[4])
                    msg.append_src(
                        Location(
                            filename=os.path.basename(
                                test_case[0]),
                            linenumber=int(
                                test_case[1]) - 1,
                            column=int(
                                test_case[2])))
                    error.msgs.append(msg)
                    errors.append(error)
        return errors


class ValgrindParser:

    @staticmethod
    def parse(input_file):
        errors = []
        tree = ET.parse(input_file)
        root = tree.getroot()
        for testcase in root.iter('error'):
            message = testcase.find('xwhat')
            # the 'error-tree' differs between having 'xwhat', 'auxwhat' (-->
            # both are extended messages) or 'what'
            error = Error(
                category=testcase.find('kind').text,
                tool='valgrind')
            if message is not None:
                msg = ErrorMessages(message.find('text').text)
            else:
                msg=ErrorMessages(testcase.find('what').text)
            # get whole stack
            for stack in testcase.iter('stack'):
                for frame in stack.iter('frame'):
                    obj = frame.find('obj')
                    if re.search(
                        '^/(usr/lib|lib|lib64|usr/local/lib)',
                            obj.text) is None:
                        if frame.find('file') is not None and frame.find(
                                'line') is not None:
                            source = Location(
                                filename=frame.find('file').text, linenumber=int(
                                    frame.find('line').text) - 1)
                            msg.append_src(source)
            error.msgs.append(msg)
            errors.append(error)
        return errors


class CMockaParser:

    @staticmethod
    def parse_cmocka_src(string: str):
        regex = re.compile(r"test-?\w*.c:\d+", 0)
        m = regex.search(string)
        if m is not None:
            string = m.group()
            print(string,sys.stderr)
            src = string.split(':')
            if len(src) == 2:
                return src
        return None

    @staticmethod
    def remove_non_printable(str):
        return ''.join(c for c in str if c.isprintable() or c == '\n')

    @staticmethod
    def parse(input_file):
        errors = []
        # read XML File to String and replace malformed data by Python’s
        # backslashed escape sequences
        # lxml is too picky with backslashed so we are doing replace and filtering everything out
        with open(input_file, 'r', encoding='utf8' , errors='replace') as IF:
            orig_msg = IF.read()
            orig_msg = orig_msg.replace("\ufffd","?")
            orig_msg = CMockaParser.remove_non_printable(orig_msg)
        root = ET.fromstring(bytes(orig_msg, encoding='utf8'))
        for testcase in root.iter('testcase'):
            # search for a failure
            failure = testcase.find('failure')
            if failure is not None:
                failure_msg_lines = failure.text.split("\n")
                error = Error(
                    category=testcase.get('name'),
                    tool='cmocka')
                msg=ErrorMessages(failure_msg_lines[0])
                if len(failure_msg_lines) == 2:
                    test_src = CMockaParser.parse_cmocka_src(
                        failure_msg_lines[1])
                    if test_src is not None:
                        try:
                            line = int(test_src[1])-1
                            file = test_src[0]
                            source = Location(
                                filename=file + ".txt", linenumber=line, file_info=False)
                            msg.append_src(source,can_fail=True)
                        except BaseException:
                            pass
                # set the 'name' of the unit-test
                error.type=ErrorType.UNITTEST
                error.kind=ErrorResult.FAILED
                error.msgs.append(msg)
                errors.append(error)
            else:
                error = Error(category=testcase.get('name'),tool='cmocka')
                # set the 'name' of the unit-test
                error.type=ErrorType.UNITTEST
                error.kind=ErrorResult.SUCCESS
                errors.append(error)
        return errors

# Currently only tested with ASAN and TSAN Reports!
class SanitizerParser:

    # for asan https://learn.microsoft.com/en-us/cpp/sanitizers/asan-error-examples?view=msvc-170
    # for tsan https://www.chromium.org/developers/testing/threadsanitizer-tsan-v2/
    regex = r"heap-use-after-free|bad-free|alloc-dealloc-mismatch|double-free|dynamic-stack-buffer-overflow|global-buffer-overflow|heap-buffer-overflow|memcpy-param-overlap|stack-buffer-overflow|stack-buffer-underflow|stack-use-after-return|stack-use-after-scope|leaked|SEGV|data race|lock-order-inversion|thread leak|use-of-uninitialized-value"

    @staticmethod
    def parse(file: str) -> Error|None:
        # sanatizer reports always only contain one error
        error = Error()

        # Open File and read content. Return None if file is empty.
        with open(file, 'r') as f:
            text = f.read()
            if (text == ''):
                return []
            
            error.raw = text

            # Separate into individual lines
            lines = text.split('\n')
            is_first_stacktrace = True
            stacktrace_has_been_read = False

            #first find Error/Warning Line for tool and primary message
            if (match := re.search(r"==[0-9]*==ERROR.*|WARNING: .*", text)) is not None:
                split_error_line = match.group(0).split(': ')
                error.type = ErrorType.ERROR
                if "WARNING" in split_error_line[0]:
                    error.kind = ErrorResult.WARNING
                else:
                    error.kind = ErrorResult.ERROR
                error.tool = split_error_line[1] # AddressSanatizer, LeakSanatizer ...
                err_msg = ErrorMessages()
                if (match := re.search(r".*(?=on.*address.*0x)", split_error_line[2])) is not None:
                    err_msg.msg=match.group(0)
                else:
                    err_msg.msg=split_error_line[2]

            else:
                print(
                    "Didn't find Error Message in Sanatizer Report, discarding: " +
                    file,
                    file=sys.stderr)
                return []

            # find summary line for type/category of error is usually given
            if (match := re.search(r"SUMMARY.*", text)) is not None:
                summary_line= match.group(0)
                p = re.search(SanitizerParser.regex, summary_line)
                if p:
                    result = p.group()
                    if result == 'leaked':
                        error.category = 'memory-leak'
                    elif result == 'SEGV':
                        error.category = 'Segmentation Fault'
                    else:
                        error.category = result
                else:
                    error.category = 'unknown'
            else:
                print(
                    "Didn't find Summary Message in Sanatizer Report, discarding: " +
                    file,
                    file=sys.stderr)
                return []
            
            error.msgs.insert(0, err_msg)

            # Line by line parsing for stack traces
            for i, line in enumerate(lines):
                
                # If the line contains a # 
                if (match:=re.search('(?<=\s\s#)[0-9]*', line)) is not None:

                    #check if it's the first frame
                    if int(match.group(0))==0:
                        if (match := re.search(r"==[0-9]*==", lines[i-1])) is not None and is_first_stacktrace:
                            #attach the stack trace to the primary message
                            new_msg = err_msg
                        else:
                            #attach the stack trace to the message above the stack trace
                            new_msg = ErrorMessages(lines[i-1])
                            error.msgs.append(new_msg)
                        is_first_stacktrace = False


                    if ' in ' in line:
                        split_stacktrace_line = line.split(' in ')[-1]
                    elif (match:=re.search('(?<=\s\s#)[0-9]*\s', line)) is not None:
                        split_stacktrace_line = line[match.end():]
                    else:
                        continue

                    # Not from our sourcecode -> Not relevant for student
                    if split_stacktrace_line.startswith('_') or (re.search('^/(usr/lib|lib|lib64|usr/local/lib)',split_stacktrace_line) is not None):
                        continue

                    method_and_location = split_stacktrace_line.split(' ')
                    location = method_and_location[1].split(':')

                    # Only the case if stacktrace not from students code
                    if (len(location) != 3):
                        continue

                    new_loc = Location(filename=location[0], linenumber=int(location[1])-1, column=int(location[2]))
                    # Append Tuple (Method: str, File: str, Row: int, Column: int) 
                    new_msg.append_src(new_loc)

            return [error]
