from __future__ import annotations
import argparse
import os
import sys
import glob
from cofee.errorManager import ErrorManager
from cofee.parser import Parser
import cofee.settings as settings
from cofee.report import Report, ReportManager
from cofee.gitlab_connector import GitlabConnector

def get_files(directory: str):
    search_string = directory + '/**/*'
    files = glob.glob(search_string, recursive=True)
    return files

def load_settings():
    try:
        settings.branch = os.environ['CI_COMMIT_BRANCH']
    except:
        settings.branch = "main"
    try:
        settings.commit_sha = os.environ['CI_COMMIT_SHA']
    except:
        settings.commit_sha = "fslakdfjslkdf"
    try:
        settings.project_dir = os.environ['CI_PROJECT_DIR']
    except:
        settings.project_dir = "./"
    try:
        settings.job_id = os.environ['CI_JOB_ID']
    except:
        settings.job_id = '7'
    try:
        settings.pipeline_iid = os.environ['CI_PIPELINE_IID']
    except:
        settings.pipeline_iid = '7'
    try:
        settings.pages_url = os.environ['CI_PAGES_URL']
    except:
        settings.pages_url = "https://gbr-2022.pages.uni-potsdam.de/gbr0/uebung-1-ringbuffer"
    try:
        settings.project_url = os.environ['CI_PROJECT_URL']
    except:
        settings.project_url = "https://google.com"
    try:
        settings.project_id = int(os.environ['CI_PROJECT_ID'])
    except:
        settings.project_id = 7634
    try:
        settings.server_url = os.environ['CI_SERVER_URL']
    except:
        settings.server_url = "https://gitup.uni-potsdam.de"

def main():

    # parse arguments
    arg_parser = argparse.ArgumentParser(
        description='CoFeUP-Parser designed to parse output of analyze-tools and '
        'generate a junit-xml with the results')
    # add group for mutual exclusion
    # group for output and test
    # arg_group = arg_parser.add_mutually_exclusive_group()
    arg_parser.add_argument(
        '--input-dir',
        # required=True,
        type=str,
        help='The input directory to parse e.g.: "/results" - All supported filetypes in the '
        'directory will be parsed. Supported filetypes are: '
        '.plist, .make, .valgrind, .tidy, .cmocka')
    arg_parser.add_argument(
        '--output-junit',
        type=str,
        help='The output file e.g.: "output.xml" - it is a junit.xml')
    arg_parser.add_argument(
        '--output-html',
        type=str,
        help='The output directory e.g.: "./output/"')
    arg_parser.add_argument(
        '--export-errors',
        type=str,
        help='The pickle file from where to import errors e.g.: "results.pkl"')
    arg_parser.add_argument(
        '--export-reports',
        type=str,
        help='The pickle file from where to import reports e.g.: "reports.pkl"')
    arg_parser.add_argument(
        '--load-errors',
        type=str,
        help='The pickle file from where to import errors e.g.: "results.pkl"')
    arg_parser.add_argument(
        '--download-reports',
        action='store_true',
        help='try to download pickle file')
    arg_parser.add_argument(
        '--with-gitlab',
        action='store_true',
        help='specifies if the gitlab connector should be used')
    arg_parser.add_argument(
        '--load-reports',
        type=str,
        help='The pickle file from where to import reports e.g.: "reports.pkl"')
    arg_parser.add_argument(
        '--create-report',
        action='store_true',
        help='The pickle file from where to import reports e.g.: "reports.pkl"')
    arg_parser.add_argument('--print', action='store_true',
                           help='Prints all errors found to std-out.')
    arg_parser.add_argument(
        '--test',
        type=str,
        help='Run tests to see if the parser is working correctly. The parser parses the whole '
        'inputdir and writes a temporary junit.xml-file. The recently created file is compared '
        'with a predefined and loaded test-file. '
        'The test-file needs to be a xml-file to run tests.')
    arg_parser.add_argument(
        '--cf_global',
        type=str,
        help='The global command file e.g.: "messages.json" - it needs to be a json- or xml-file. '
        'If a local command-file is given, the global one will be overridden.')
    arg_parser.add_argument(
        '--cf_local',
        type=str,
        help='The local command file e.g.: "messages.xml" - it needs to be a json- or xml-file. '
        'If a local command-file is given, the global one will be overridden.')
    arg_parser.add_argument(
        '--srcdir',
        type=str,
        help='The directory where src files for the reports are located. ')
    arg_parser.add_argument(
        '--template-dir',
        type=str,
        help='The directory where jinja files for the html reports are located. ')

    args = arg_parser.parse_args()
    load_settings()

    # print(files)
    files=[]
    errors = ErrorManager()
    reports = ReportManager()
    if args.with_gitlab:
        gitlab = GitlabConnector(private_token='XXX', url=settings.server_url, project_id=settings.project_id, pages_url=settings.pages_url )

    # start processing
    if args.input_dir:
        files = get_files(args.input_dir)
    if args.srcdir is not None:
        if args.srcdir == "./":
            settings.srcdir = ""
        else:
            settings.srcdir = args.srcdir
        
    if args.cf_local is not None:
        errors.add_hint(args.cf_local)
    # global command-file second

    if args.cf_global is not None:
        errors.add_hint(args.cf_global)
    # start parsing

    for file in files:
        errors.concat_errors(Parser.parse(file))
    # local command-file first

    if args.load_errors:
        if os.path.isdir(args.load_errors):
            search_string = args.load_errors + '/*.pkl'
            files = glob.glob(search_string, recursive=True)
        else:
            files = [args.load_errors]
        for fpath in files:
            with open(fpath, 'rb') as f:
                importstr= f.read()
            print("Trying to import Errors from file: "+ fpath, sys.stderr)
            errors.import_from_str(importstr)

    if args.export_errors:
        with open(args.export_errors, 'wb') as f:
            f.write(errors.export_to_str())

    if args.create_report:
        rep=Report(errors=errors.errors,commit_sha=settings.commit_sha,pipeline_iid=settings.pipeline_iid,branch=settings.branch)
        reports.reports.append(rep)

    if args.load_reports:
        with open(args.load_reports, 'rb') as f:
            importstr= f.read()
        reports.import_from_str(importstr)

    if args.download_reports:
        if args.with_gitlab:
            print("Trying to import Errors from download", sys.stderr)
            data=gitlab.get_previous_results_via_api()
            if data is not None:
                reports.import_from_str(data)
        else:
            print("--download-reports requires --with-gitlab!\n ", sys.stderr)
            arg_parser.print_help()
            sys.exit(2)

    if args.export_reports:
        with open(args.export_reports, 'wb') as f:
            f.write(reports.export_to_str())

    if args.print:
        errors.print_errors()

    if args.test:
        errors.compare_errors(args.test)

    if args.output_junit:
        errors.write_junit(args.output_junit)

    if args.output_html:
        if args.template_dir:
            reports.generate_html(args.template_dir,args.output_html)
        else:
            print("--output-html requires --template-dir!\n ", sys.stderr)
            arg_parser.print_help()
            sys.exit(2)

    if args.with_gitlab:
        gitlab.update_project_description("CoFee Ergebnisse: "+ settings.pages_url)
            

if __name__ == '__main__':
    main()
