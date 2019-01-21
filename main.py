import frontmatter
import yaml 
import json
import requests
from bs4 import BeautifulSoup


class GenerateProjectPages:
    """
        This class generates the projects pages for Linaro.org based on current projects and projects
        from patches.linaro.org
    """
    def __init__(self):

        # Main unique projects list
        self.projects = []
        self.uniqueProjectIdentifiers = []
        self.main()

    def main(self):
        """
            Collect the projects from projects.yml and projects.json
            and output unique markdown pages with the relevant keys to pull stats
            from patches.linaro.org
        """
        self.getJSONProjects()
        self.aggregateProjects()
        self.generateMarkdownFiles()
        print(self.projects)
        # self.getYAMLProjects()

    def aggregateProjects(self):

        """ Takes the self.projects list and aggregates projects based on the project_link_name"""
        self.uniqueProjectIdentifiers = []
        for project in self.projects:
            if "-" in project["project_link_name"]:
                projectIdentifier = project["project_link_name"].split("-")[0]
                if projectIdentifier not in self.uniqueProjectIdentifiers:
                    self.uniqueProjectIdentifiers.append(projectIdentifier)
            elif "_" in project["project_link_name"]:
                projectIdentifier = project["project_link_name"].split("_")[0]
                if projectIdentifier not in self.uniqueProjectIdentifiers:
                    self.uniqueProjectIdentifiers.append(projectIdentifier)
        print(self.uniqueProjectIdentifiers)
        input()
                
    def getJSONProjects(self):
        """ Get projects from projects.yml and appends to self.projects"""
        with open("projects.json") as data:
            try:
                projects_json = json.load(data)
                for project in projects_json:
                    # Collect useful and valid data from patches projects.json
                    projectName = ""
                    projectLinkName = ""
                    projectUrl = ""
                    projectScmUrl = ""
                    projectMaintainers = ""
                    projectEmail = ""
                    projectPatchesUrl = ""

                    if project["name"] != "":
                        projectName = project["name"]
                    if project["link_name"] != "":
                        projectLinkName = project["link_name"]
                    if project["webscm_url"].lower() != "n/a" or project["webscm_url"] != "":
                        projectUrl = project["webscm_url"]
                    if project["scm_url"].lower() != "n/a" or project["scm_url"] != "":
                        projectScmUrl = project["scm_url"]
                    if project["maintainers"] != "" and len(project["maintainers"]) > 0:
                        projectMaintainers = project["maintainers"]
                    if project["list_email"].lower() != "n/a" or project["list_email"] != "":
                        projectEmail = project["list_email"]
                    if project["url"] != "":
                        projectPatchesUrl = project["url"]
                    
                    # Create a new dict to append to self.projects
                    newProject = {
                        "project_name": projectName,
                        "project_link_name": projectLinkName,
                        "project_url": projectUrl,
                        "project_maintainers": projectMaintainers,
                        "project_scm_url": projectScmUrl,
                        "project_email": projectEmail,
                        "project_patches_url": projectPatchesUrl
                    }
                    # Append to self.projects
                    self.projects.append(newProject)

            except Exception as e:
                print(e)

    def generateMarkdownFiles(self):

        """
            Generates the projects based on self.projects aggregated list from yml/json
        """
        identifiers = self.uniqueProjectIdentifiers
        changedProjects = self.projects
        for project in changedProjects:

            projectNameIdentifier = ""
            if "-" in project["project_link_name"]:
                projectNameIdentifier = project["project_link_name"].split("-")[0]
                splitChar = "-"
            elif "_" in project["project_link_name"]:
                projectNameIdentifier = project["project_link_name"].split("_")[0]
                splitChar = "_"


            if projectNameIdentifier != "" and projectNameIdentifier in identifiers:
                subProjects = []
                for sub_project in changedProjects:
                    if projectNameIdentifier in sub_project["project_link_name"].split(splitChar):
                        subProjects.append(sub_project)
                # Remove the identifier from the uniqueProjectIdentifiers to ignore
                identifiers.remove(projectNameIdentifier)
                # Open a new file based on the template.md file
                with open("template.md","r") as md_file:
                    front_matter = frontmatter.loads(md_file.read())

                    front_matter["title"] = projectNameIdentifier
                    front_matter["sub_projects"] = subProjects

                    file_name = projectNameIdentifier.lower() +  ".md"
                    output_object = "projects/" + file_name
                    # Create the new post object and write the front matter to post.
                    with open(output_object,"w") as new_post_file:
                        new_post_file.writelines(frontmatter.dumps(front_matter))
                        print("Jekyll project created for {0} at {1}".format(project["project_name"], output_object))
            else:
                if projectNameIdentifier == "" and projectNameIdentifier not in identifiers:
                    # Open a new file based on the template.md file
                    with open("template.md","r") as md_file:
                        front_matter = frontmatter.loads(md_file.read())
                        # Add front matter attributes
                        # Create a new dict to append to self.projects
                        # newProject = {
                        #     "project_name": projectName,
                        #     "project_link_name": projectLinkName,
                        #     "project_url": projectUrl,
                        #     "project_maintainers": projectMaintainers,
                        #     "project_scm_url": projectScmUrl,
                        #     "project_email": projectEmail,
                        #     "project_patches_url": projectPatchesUrl
                        # }
                        if project["project_name"] != "":
                            front_matter["title"] = project["project_name"]
                        if project["project_link_name"] != "":
                            front_matter["link_name"] = project["project_link_name"]
                        if project["project_url"] != "":
                            front_matter["project_url"] = project["project_url"]
                        if project["project_maintainers"] != "":
                            front_matter["project_maintainers"] = project["project_maintainers"]

                        file_name = project["project_link_name"].replace(" ", "-").lower() +  ".md"
                        output_object = "projects/" + file_name
                        # Create the new post object and write the front matter to post.
                        with open(output_object,"w") as new_post_file:
                            new_post_file.writelines(frontmatter.dumps(front_matter))
                            print("Jekyll project created for {0} at {1}".format(project["project_name"], output_object))

    def getYAMLProjects(self):
        """ Get projects from projects.yml and appends to self.projects"""
        with open("projects.yml", 'r') as stream:
            try:
                yaml_data = yaml.safe_load(stream)
                for each in yaml_data:
                    md_file = frontmatter.loads(open("template.md","r").read())
                    # Add front matter attributes
                    md_file['title'] = each["name"]
                    md_file['image'] = "/assets/images/projects/" + each["image"]
                    # Prepend the output folder and the new_post_name
                    file_name = each["name"].replace(" ", "-").lower() +  ".md"
                    if each["url"]:
                        md_file["url"] = each["url"]
                        # response = requests.get(each["url"])
                        # soup = BeautifulSoup(response.text, features="html.parser")
                        # metas = soup.find_all('meta')
                        # description = [ meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description' ]
                        # if len(description) > 0:
                        #     md_file["description"] = '"{0}"'.format(description[0])
                    output_object = "projects/" + file_name
                    # Create the new post object and write the front matter to post.
                    with open(output_object,"w") as new_post_file:
                        new_post_file.writelines(frontmatter.dumps(md_file))
                        print("Jekyll project created for {0} at {1}".format(each["name"], output_object))
            except yaml.YAMLError as exc:
                print(exc)

if __name__ == "__main__":
    projectPages = GenerateProjectPages()