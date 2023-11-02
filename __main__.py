# Steps
# 1 - Take a random SH Github repo
# 2 - Check if there is the database (when the database is created)
# 3 - if database created, check md5. If not retrieve directly the README
# 4 - Take the README and send it via API to the Model
import os
import requests
import json
from random import seed
from random import randint

# seed(1)

def getMaxIdRepo():
    newestGithubRepo = NewestRepo.split('https://github.com/')[1]
    resp = requests.get(f"https://api.github.com/repos/{newestGithubRepo}", headers = header)

    idNewestRepo = None
    try:
        if (resp.status_code == 200):
            print(resp.json()['id'])
            idNewestRepo = resp.json()['id']
        else:
            print(f"{newestGithubRepo} resulted in {resp}")
    except:
        print(f"Could not find ID in {newestGithubRepo}")
    return idNewestRepo

def randomRepo(maxRepoId):
    repoId = randint(0, maxRepoId)
    githubUrl = None
    print(repoId)
    # From the Repository Id, take the path from Github
    reposUrl = f"https://api.github.com/repositories/{repoId}"
    response = requests.get(reposUrl, headers = header)

    if (response.status_code == 200):
        githubUrl = response.json()['full_name']
    else:
        print(f"Github repo with Id {repoId} resulted in {response}")

    return githubUrl

def retrieveReadMe(randomGithubPath):
    # Gather the README.md
    readme_dict = None
    try:
        reposUrl = f"https://raw.githubusercontent.com/{randomGithubPath}/master/README.md"
        response = requests.get(reposUrl, headers = header)
        if (response.status_code == 200):
            readme_dict = response.text
        else:
            print(f"Github with Path '{randomGithubPath}' resulted in {response}")
    except:
        print(f"Could not find READ.me in Path '{randomGithubPath}'")
    return readme_dict

def retrieveRandomReadMe():
    idMaxRepo= getMaxIdRepo()
    if not idMaxRepo:
        return
    randomGithubPath = randomRepo(idMaxRepo)    # Get Random repo
    if not randomGithubPath:
        return
    readMe = retrieveReadMe(randomGithubPath)
    if not readMe:
        return
    return randomGithubPath, readMe

def confVariables():
    githubToken = os.getenv('GITHUB_TOKEN', default='')
    header = {'Authorization': 'Bearer ' + githubToken}
    NewestRepo = os.getenv('NEWEST_REPO', default='https://github.com/SergiAguilo/SH-Worker')
    return header, NewestRepo

if __name__ == '__main__':
    # Put your the url of your newest repository
    header, NewestRepo = confVariables()

    # retrieve the readme
    randomGithubPath, readMe = retrieveRandomReadMe()

    # send the readme to the model
    modelUrl = f"http://localhost:5800/predict"
    body = {
        "content": readMe,
        "url": randomGithubPath
    }
    response = requests.get(modelUrl, data = body )
    responsej = response.json()
    # get the metadata
    if responsej["prediction"]=="bioinformatics": # Extract metadata
        metadataUrl = f"http://localhost:5300/metadata?threshold=0.7&ignore_classifiers=false"
        body = {
            "content": readMe
        }
        response = requests.get(metadataUrl, data = body )
        responsej = response.json()
        print(responsej)
        print('A bioiformatics repo was found')
    else:
        pass

    # save the metadata in the database
    
