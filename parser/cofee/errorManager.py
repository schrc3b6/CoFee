from __future__ import annotations
from cofee.types import ErrorType,ErrorResult
from cofee.hint import Hint 
from cofee.hint import HintManager 
from cofee.error import Error
import os
from lxml import etree as ET
import json
import hashlib
import hmac
import pickle
import sys

class ErrorManager:

    def __init__(self, errors=None):
        if errors is None:
            self.__errors = []
        else:
            self.__errors = errors
        self.__cm = HintManager()

    def __iter__(self):
        return self.__errors.__iter__()

    def __len__(self):
        return len(self.__errors)

    @property
    def errors(self):
        return self.__errors

    @property
    def hm(self):
        return self.__cm

    @errors.deleter
    def errors(self):
        del self.__errors

    # TODO run generate_error_msg and operate on junit creation
    def add_error(self, error: Error):
        # error.generate_error_msg();
        error.hint = self.__cm.get_hint(error.tool, error.category)
        error.extend_hint()
        if error.type == ErrorType.UNITTEST: 
            if error.hint is None:
                raise ValueError("Unit Test requires an Hint category:" + error.category)
            if error.kind is not ErrorResult.SUCCESS and error.hint.unit_test_src is None and len(error.msgs[0].locations) > 0:
                error.msgs[0].locations[0].codelines=None
            elif error.kind is not ErrorResult.SUCCESS and len(error.msgs[0].locations) > 0:
                error.msgs[0].locations[0].codelines= error.hint.unit_test_src
        if error is not None:
            self.__errors.append(error)

    def concat_errors(self, errors):
        for error in errors:
            self.add_error(error) 

    def pop_error(self, pos: int):
        self.__errors.pop(pos)

    def add_hint(self, hint_file):
        extension = os.path.splitext(hint_file)
        if extension[1] == '.json':
            raise NotImplementedError("Json Hints are deprecated")
            # with open(hint_file, 'r') as EF:
            #     root = json.load(EF)
            #     message_type = root.get('message_type')
            #     for kind in message_type.items():
            #         # It's a tuple - first item is the name and the second item
            #         # is the error_type-tuple
            #         for test_case in kind[1].items():
            #             self.__cm.add_hint(
            #                 Hint(
            #                     kind[0],
            #                     test_case[0],
            #                     test_case[1]['action'],
            #                     test_case[1]['msg']))
        elif extension[1] == '.xml':
            with open(hint_file, 'r') as EF:
                root = ET.parse(EF)
                message_type = root.getroot()
                for tool in message_type: # tool
                    for category in tool: # category
                        error_action = category.find('action')
                        error_msg = category.find('msg')
                        error_testsrc = category.find('unit_test_src')
                        if error_testsrc is not None:
                            error_testsrc = error_testsrc.text
                        error_line = category.find('line')
                        if error_line is not None:
                            error_line_start = int(error_line.find('start').text)
                            error_line_end = int(error_line.find('end').text)
                        else:
                            error_line_start = None
                            error_line_end = None
                        self.__cm.add_hint(
                            Hint(
                                tool.tag,
                                category.attrib.get('Name'),
                                error_action.text,
                                error_msg.text,
                                unit_test_src=error_testsrc,
                                start_line=error_line_start,
                                end_line=error_line_end
                            ))
        else:
            print('Hint-file needs to be xml or json!')

    # def operate(self,error):
    #     hint = self.__cm.get_hint(error.tool, error.category)
    #     if hint is not None:
    #         if hint.action == 'replace':
    #             error.error_msg = hint.error_msg
    #         if hint.action == 'replaceall':
    #             error.error_msg = hint.error_msg
    #             error.error_srcs.clear();
    #         if hint.action == 'prepend':
    #             error.prepend_error_msg('\n')
    #             error.prepend_error_msg('\n')
    #             error.prepend_error_msg(hint.error_msg)
    #         if hint.action == 'append':
    #     error.append_error_msg('\n')
    #             error.append_error_msg(hint.error_msg)
    #         if hint.action == 'delete':
    #             return None
    #     return error

    def print_errors(self):
        for error in self.__errors:
            error.print_error()

    def error_count(self):
        count = 0
        for error in self.__errors:
            if error.kind is not ErrorResult.SUCCESS:
                count += 1
        return count

    # def compare_errors(self, test_file: str):
    #     # write a junit-xml to test most important functions of the parser and
    #     # import it as string to compare it
    #     self.write_junit('testing.xml')
    #     with open('testing.xml', 'r') as TF1:
    #         root = ET.parse(TF1)
    #         root = root.getroot()
    #         dict1 = ET.tostring(root)
    #     os.remove('testing.xml')
    #     with open(test_file, 'r') as TF2:
    #         root = ET.parse(TF2)
    #         root = root.getroot()
    #         dict2 = ET.tostring(root)
    #     if dict1 == dict2:
    #         print("\nSUCCESS - The errors from the inputdir are EQUAL to the test-file!")
    #     else:
    #         print(
    #             "\nFAILED - The errors from the inputdir are NOT EQUAL to the test-file!")

    def generateTestCases(self, root):
        error_index = 0
        for error in self:
            if error.kind == ErrorResult.SUCCESS:
                ET.SubElement(
                    root,
                    "testcase",
                    classname="CoFee_UP",
                    name=error.title,
                    # name=error.error_name +
                    # ' - ' +
                    # error.error_type,
                    time="0")
            else:
                error_index += 1
                testcase = ET.SubElement(
                    root,
                    "testcase",
                    classname="CoFee_UP",
                    name = error.title + ' - '+ str(error_index), 
                    # name=error.error_name +
                    # str(error_index) + ' - ' +
                    # error.error_type,
                    time="0")
                errorElement = ET.SubElement(
                    testcase, "error", type=error.category)
                errorElement.text = ET.CDATA("\n" + error.generate_error_msg() + "\n")

    def write_junit(self, output_file: str):
        errorcount = self.error_count()
        # generat Junit root tag
        root = ET.Element(
            "testsuite",
            name="CoFee_UP",
            test=str(
                len(self)),
            errors=str(errorcount),
            failure="0",
            skip="0")
        if errorcount == 0:
            # add no error tag
            ET.SubElement(
                root,
                "testcase",
                classname="CoFee_UP",
                name="Success - 0 Errors found",
                time="0")
        else:
            self.generateTestCases(root)
        # write XML to file
        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(output_file, xml_declaration=True, encoding='utf-8')

    def import_from_str(self, import_str):
        digest, data = import_str.split(b' ',1)
        digest= digest.decode('utf-8')
        expected_digest = hmac.new(b'cofeeup_em', data, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, expected_digest):
            print( "Importing Errors from Str: Corrupted import!" ,
                file=sys.stderr)
            return
        errm = pickle.loads(data)
        self.__errors = self.errors + errm.errors
        self.__cm.merge(errm.hm)

    def export_to_str(self):
        data = pickle.dumps(self)
        digest = hmac.new(b'cofeeup_em', data, hashlib.sha256).hexdigest()
        return digest.encode('utf-8') + b' ' + data

