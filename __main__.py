# Steps
# 1 - Take a random SH Github repo
# 2 - Check if there is the database (when the database is created)
# 3 - if database created, check md5. If not retrieve directly the README
# 4 - Take the README and send it via API to the Model
import os
import requests
import json
import logging
from time import sleep
from datetime import datetime
from random import seed
from random import randint
from dotenv import load_dotenv
from pymongo import MongoClient

def connectMongo():
    # variables come from .env file
    mongoHost = os.getenv('MONGO_HOST', default='localhost')
    mongoPort = os.getenv('MONGO_PORT', default='27017')
    mongoUser = os.getenv('MONGO_USER')
    mongoPass = os.getenv('MONGO_PWD')
    mongoAuthSrc = os.getenv('MONGO_AUTH_SRC', default='admin')
    mongoDb = os.getenv('MONGO_DB', default='oeb-research-software')
    mongoCollection = os.getenv('MONGO_COLLECTION', default='githubMiner')

    # Connect to MongoDB
    mongoClient = MongoClient(
        host=mongoHost,
        port=int(mongoPort),
        username=mongoUser,
        password=mongoPass,
        authSource=mongoAuthSrc,
    )
    db = mongoClient[mongoDb]
    collection = db[mongoCollection]
    print(list(collection.find()))
    return collection

# seed(1)

def getMaxIdRepo():
    newestGithubRepo = NewestRepo.split('https://github.com/')[1]
    url = f'https://api.github.com/repos/{newestGithubRepo}'
    resp = requests.get(url, headers = header)

    idNewestRepo = None
    try:
        if (resp.status_code == 200):
            print(resp.json()['id'])
            idNewestRepo = resp.json()['id']
            logging.info(f'ID of newest repo is {idNewestRepo}')
        else:
            logging.error(f'Could not retrieve ID of newest repo. {url} resulted in {resp}')
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
        resp = response.json()
        print(resp)

    return githubUrl

def retrieveReadMe(randomGithubPath):
    # Gather the README.md
    readme_dict = {}
    try:
        reposUrl = f"https://raw.githubusercontent.com/{randomGithubPath}/master/README.md"
        response = requests.get(reposUrl, headers = header)
        if (response.status_code == 200):
            readme_dict = response.text
        else:
            print(f"readme of repo with Path '{randomGithubPath}' resulted in {response}")
    except:
        print(f"Could not find READ.me in Path '{randomGithubPath}'")
    return readme_dict

def retrieveRandomReadMe():
    idMaxRepo= getMaxIdRepo()
    if not idMaxRepo:
        raise Exception('No idMaxRepo! Aborting...')

    readMe = ''

    while not readMe: 
        # Get Random repo
        randomGithubPath = randomRepo(idMaxRepo)  # Can fail bc Id belong to private repo

        if randomGithubPath:
            # Get readme of repo
            readMe = retrieveReadMe(randomGithubPath) # Can fail bc README.md does not exist in the repo
            if not readMe:
                logging.info('No readMe')
        else:
            logging.info('No randomGithubPath')
        

    return randomGithubPath, readMe

def confVariables():
    githubToken = os.getenv('GITHUB_TOKEN', default='')
    header = {'Authorization': 'Bearer ' + githubToken}
    NewestRepo = os.getenv('NEWEST_REPO', default='https://github.com/SergiAguilo/SH-Worker')
    return header, NewestRepo



def getOneRespositoryPrediction():
    # retrieve the readme
    randomGithubPath, readMe = retrieveRandomReadMe()

    # send the readme to the model
    modelUrl = f"http://sh-model-api:5800/predict"
    body = {
        "content": readMe,
        "url": f"https:github.com/{randomGithubPath}"
    }
    response = requests.post(modelUrl, json = body )
    responsej = response.json()
    # get the metadata
    print(responsej)
    doc = {
        "url": f"https:github.com/{randomGithubPath}",
        "ouwner": randomGithubPath.split('/')[0],
        "repo": randomGithubPath.split('/')[1],
        "prediction": responsej["prediction"],
        "confidence": responsej["confidence"],
        "model": "bioinforRepo_Bert",
        "readme": readMe,
        "date": datetime.now()
    }
    
    if responsej["prediction"]=="bioinformatics" and responsej["confidence"]>0.9: # Extract metadata
        metadataUrl = f"http:somef-api:5300/metadata?threshold=0.7&ignore_classifiers=false"
        body = {
            "content": readMe
        }
        response = requests.post(metadataUrl, data = body )
        responsej = response.json()
        doc['metadata'] = responsej
        
    # save the metadata in the database
    collection = connectMongo()
    x = collection.insert_one(doc)
    

if __name__ == '__main__':
    # load env variables
    load_dotenv()
    sleep(5) # gives time to the other services to start

    # Put your the url of your newest repository
    header, NewestRepo = confVariables()

    # Process 10 repositories with readme

    for i in range(10):
        getOneRespositoryPrediction()
        sleep(1)
    


    
