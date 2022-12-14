from __future__ import annotations
import gitlab
import requests

class GitlabConnector:

    def __init__(self, private_token: str = "", url: str = "", project_id: int=0, pages_url: str = ""):
        self.private_token = private_token
        self.url = url
        self.project_id = project_id
        self.pages_url = pages_url
        self.gl = gitlab.Gitlab(url=url,private_token=private_token)
        self.gl.auth()
        self.project = self.gl.projects.get(self.project_id)

    def update_project_description(self, desciption: str|None = None):
        self.project.description = desciption
        self.project.save()

    def update_readme(self, content: str):
        data={
          "branch": "master",
          "commit_message": "update readme",
          "actions": [
            {
              "action": "update",
              "file_path": "README.md",
                    "content": content
            },
          ]
        }
        commit = self.project.commits.create(data)

    def get_previous_results(self):
        response = requests.get(self.pages_url+'/cofee.pkl')
        if response.status_code == 200:
            return response.content
        else:
            return None
        
    def get_previous_results_via_api(self):
        jobs=self.project.jobs.list(all=True)
        jobs = [x for x in jobs if x.name == "pages"]
        jobs.sort(key=lambda x:x.id, reverse=True)
        for job in jobs:
            found=False
            for artifact in job.attributes['artifacts']:
                if artifact['filename'] == 'artifacts.zip':
                    found=True
            if found:
                try:
                    data = job.artifact('public/cofee.pkl')
                except:
                    data = None
                if data is not None:
                    return data
        return None

        # artifacts.raw('main', 'public/cofee.pkl', 'pages')
        # print(art)

