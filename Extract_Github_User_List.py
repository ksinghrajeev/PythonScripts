# This script extacts github user list into an excel file.
# This was required to be shared with the end client to show,
# who all has access to code repo and with what permission.

import os
import pandas as pd
import json
from datetime import datetime
import re

basePath = os.path.dirname(os.path.abspath(__file__))
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
nonspace = re.compile(r'\S')
fileName = 'User_List_' + dt_string
filePath = basePath + '/' + fileName

# example - /repos/rajeev/homeproject/collaborators
repoName = 'mention your report name'

command = 'gh api -per_page=100 -page=2000 --paginate -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" ' + repoName + ' > ' + fileName + '.json'

print(command)

def iterparse(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = nonspace.search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded

def main():
    try:
        os.system(command)
    except:
        print("Something went wrong")
        
    jsonFile = open(filePath + '.json', 'r', encoding="utf8")
    contents = list(iterparse(jsonFile.read())) #Get all JSON as List i.e. handling ][{
    length = len(contents)
    dfs = [] 
    for i in range(length):    
        data = pd.json_normalize(contents[i]) #normalize individual JSON
        dfs.append(data) 
        
    temp = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.
    temp.to_excel(filePath + '.xlsx')

if __name__ == "__main__":
    main()