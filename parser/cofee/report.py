from __future__ import annotations
from cofee.error import Error
from cofee.types import ErrorResult
from jinja2 import Template, FileSystemLoader, Environment, select_autoescape
from typing import List
import pickle
import hashlib
import hmac
import sys
import cofee.settings as settings

class Report:

    def __init__(self, errors: List[Error]=None, commit_sha: str ="", pipeline_iid: int = 0, branch: str =""):
        self.commit_sha=commit_sha
        self.pipeline_iid=pipeline_iid
        self.branch=branch
        self.project_url=settings.project_url
        if errors==None:
            self.errors=[]
        else:
            self.errors=errors
        
    def get_tools(self):
        tools= set()
        for error in self.errors:
            tools.add(error.tool)
        return tools

    def get_errors_by_tool(self):
        error_dict=dict()
        for tool in self.get_tools():
            error_dict[tool]=[]
        for error in self.errors:
            error_dict[error.tool].append(error)
        if "cmocka" in error_dict:
            error_dict["cmocka"].sort(key=lambda x: x.kind.value)
        return error_dict

    def get_status(errors:List[Error]=[]):
        worst = 10
        if not errors:
            return "failed"
        for error in errors:
            if error.kind.value < worst:
                worst = error.kind.value
        if worst == ErrorResult.FAILED.value:
            worst = ErrorResult.ERROR.value
        return ErrorResult(worst).name.lower()
    
    @property
    def tools(self):
        return self.get_tools()
    
    @property
    def errors_by_tool(self):
        return self.get_errors_by_tool()

    @property
    def results_by_tool(self):
        errs=self.get_errors_by_tool()
        res= dict()
        for key in errs:
            results= dict()
            for err in errs[key]:
                if err.kind.name in results:    
                    results[err.kind.name]+=1
                else:
                    results[err.kind.name]=1
            res[key]= results
        return res
        
    @property
    def status_by_tool(self):
        errs=self.get_errors_by_tool()
        stats= dict()
        for key in errs:
            stats[key]= Report.get_status(errs[key])
        return stats

    @property
    def pipeline_status(self):
        return Report.get_status(self.errors)


def tool_to_name(value):
    if value == "cmocka":
        return "UnitTests"
    if value == "makecmocka":
        return "UnitTests Build"
    if value == 'static-analyzer':
        return "Static Analysis"
    if value == 'makefile':
        return 'Compiler'
    if value == 'clang-tidy':
        return 'Linter'
    return value

def to_icon(value):
    if value == "WARNING":
        return """<span class="text-warning"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle" viewBox="0 0 16 16">
<path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/>
<path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995z"/>
</svg></span>"""
    elif value == "SUCCESS":
        return """<span class="text-success"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">
<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
<path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
</svg></span>"""
    return """<span class="text-danger"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="align-middle bi bi-x-circle" viewBox="0 0 16 16">
<path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
<path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z" />
</svg></span>"""

class ReportManager:
    
    def __init__(self, reports: List[Report]=None, import_str: str|None= None):
        self.reports=[]
        if import_str:
            import_from_str( import_str)
        if reports:
            self.reports + reports

    def import_from_str(self, import_str):
        digest, data = import_str.split(b' ',1)
        digest= digest.decode('utf-8')
        expected_digest = hmac.new(b'cofeeup_rep', data, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, expected_digest):
            print( "Importing Errors from Str: Corrupted import!" ,
                file=sys.stderr)
            return
        reportm = pickle.loads(data)
        self.reports = self.reports + reportm.reports

    def export_to_str(self):
        data = pickle.dumps(self)
        digest = hmac.new(b'cofeeup_rep', data, hashlib.sha256).hexdigest()
        return digest.encode('utf-8') + b' ' + data

    def generate_numbers(self):
        for report in self.reports:
            for ie, error in enumerate(report.errors):
                error.nr = ie+1
                for im, msg in enumerate(error.msgs):
                    msg.nr = im+1
                    for il, location in enumerate(msg.locations):
                        location.nr = il+1

    def generate_html(self, templates: str ,path: str):
        self.reports.sort(key=lambda x: int(x.pipeline_iid),reverse=True)
        self.generate_numbers()
        env = Environment( loader=FileSystemLoader(templates), autoescape=select_autoescape())
        env.filters['to_icon']= to_icon
        env.filters['tool_to_name']= tool_to_name
        t_index = env.get_template("index.html")
        t_report = env.get_template("report.html")
        res =t_index.render(reports=self.reports)
        with open(path+"/index.html", 'w') as f:
            f.write(res)
        for report in self.reports:
            res =t_report.render(report=report)
            pipeline_path=path+"/"+str(report.pipeline_iid)+".html"
            with open(path+"/"+str(report.pipeline_iid)+".html", 'w') as f:
                f.write(res)
        pass
