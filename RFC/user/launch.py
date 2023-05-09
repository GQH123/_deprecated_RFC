from .project.ProjectConfig import ProjectConfig
from .project.Project import Project

def launch_project(
    project_config: ProjectConfig
):
    project = Project(project_config)
    project.launch()