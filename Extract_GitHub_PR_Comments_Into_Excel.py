# This script create a report to judge the effectiveness of code review for all PR in github. 
# It uses "gh API" to extract data from Github repo.

# 1. Extract all data from github
# 2. Create Dataframe with all data
# 3. Create final dataframe based on data from 3 dataframe
# 4. Write into excel

import os
import re
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
import pathlib
import traceback


basePath = os.path.dirname(os.path.abspath(__file__))
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
#dt_string= "01_10_2022_19_03_56"
nonspace = re.compile(r'\S')

pr_base_link = 'https://github.ibm.com/api/v3/repos/anviswa1/melco-ec/pulls/'
pr_FileName = 'PR_' + dt_string
pr_Comment_FileName = 'PR_comments_' + dt_string

pathSeparator = '\\'
jsonExtension = '.json'
excelExtension = '.xlsx'
unwantedColumns = ['node_id','url','diff_url','patch_url','issue_url','commits_url','review_comments_url','review_comment_url','comments_url', 'head.label','base.label','requested_teams','user.node_id','user.avatar_url','user.html_url','assignee.login','assignee.id','assignee.node_id','assignee.avatar_url','assignee.html_url','_links.html.href','diff_hunk','patch']

base_command = 'gh api -per_page=100 -page=2000 --paginate -H "Accept: application/vnd.github.v3.raw+json" /repos/ksinghrajeev/xyz/'
command_to_extract_pr = base_command + 'pulls?state=closed  > ' + pr_FileName + jsonExtension
command_to_extract_pr_comments = base_command + 'pulls/comments > ' + pr_Comment_FileName + jsonExtension


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


def create_extension_df():
    ext_consideration = [('aird','No'),('build','No'),('class','No'),('classpath','No'),('cms','No'),('csv','No'),('gif','No'),('gitignore','No'),('jar','No'),('jpeg','No'),
            ('jpg','No'),('launch','No'),('pem','No'),('pfx','No'),('pkcs8','No'),('pmd','No'),('png','No'),('prefs','No'),('project','No'),
            ('properties','No'),('springBeans','No'),('svg','No'),('trc','No'),('uml','No'),('xmi','No'),
            ('css','Yes'),('html','Yes'),('iml','Yes'),('impex','Yes'),('java','Yes'),('js','Yes'),('json','Yes'),('jsp','Yes'),('less','Yes'),('md','Yes'),('sh','Yes'),('tag','Yes'),
            ('tld','Yes'),('ttc','Yes'),('txt','Yes'),('vm','Yes'), ('xml','Yes'),('xsd','Yes'),('','No')
            ]
    
    temp = pd.DataFrame(ext_consideration, columns=['extension', 'consideration'])
    
    return temp


def resize_column(df, sheetName, writer):
    worksheet = writer.sheets[sheetName]  # pull worksheet object
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name)) + 1   # len of column name/header
                    )) + 1  # adding a little extra space
        worksheet.set_column(idx +1, idx+1, max_len)  # set column width

def find_columns_having_same_value_in_all_row(df):
    # check which columns error when counting number of uniques
    ls_cols_nunique = []
    ls_cols_error_nunique = []
    for each_col in df.columns:
        try:
            df[each_col].nunique()
            ls_cols_nunique.append(each_col)
        except:
            ls_cols_error_nunique.append(each_col)

    return  df[ls_cols_nunique].nunique()
    

def create_sprint_df():
    sprint = [  ('Sprint-1','20-Mar-2022','15-Apr-2022'),
                ('Sprint-2','18-Apr-2022','02-May-2022'),
                ('Sprint-3','03-May-2022','20-May-2022'),
                ('Sprint-4','21-May-2022','10-Jun-2022'),
                ('Sprint-5','11-Jun-2022','01-Jul-2022'),
                ('Sprint-6','02-Jul-2022','25-Jul-2022'),
                ('Sprint-7','26-Jul-2022','23-Aug-2022')
             ]
               
    sprint_df = pd.DataFrame(sprint, columns = ['Sprint', 'Start_Date','End_Date'])
    sprint_df ['Start_Date'] = pd.to_datetime( sprint_df ['Start_Date'], errors='coerce', utc=True).dt.strftime('%d-%m-%Y')
    sprint_df ['End_Date'] = pd.to_datetime( sprint_df ['End_Date'], errors='coerce', utc=True).dt.strftime('%d-%m-%Y')
    sprint_df ['Days'] = '=NETWORKDAYS(INDIRECT("C"&ROW()),INDIRECT("D"&ROW()))'
    sprint_df['Reviewer_Comments'] = '=SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C" & Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"master")*(Consolidation!$H$2:$H$3000<>"master")*Consolidation!$M$2:$M$3000) + SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C" & Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"dev")*(Consolidation!$H$2:$H$3000="master")*Consolidation!$M$2:$M$3000)'
    sprint_df['Reviewee_Comments'] = '=SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C" & Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"master")*(Consolidation!$H$2:$H$3000<>"master")*Consolidation!$N$2:$N$3000) + SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C" & Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"dev")*(Consolidation!$H$2:$H$3000="master")*Consolidation!$N$2:$N$3000)'
    sprint_df['Lines_Of_Code'] = '=(SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C"& Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"master")*(Consolidation!$H$2:$H$3000<>"master")*Consolidation!$L$2:$L$3000) + SUMPRODUCT((Consolidation!$F$2:$F$3000>=INDIRECT("$C"& Row()))*(Consolidation!$D$2:$D$3000<>363073)*(Consolidation!$F$2:$F$3000<=INDIRECT("$D" & Row()))*(Consolidation!$G$2:$G$3000<>"dev")*(Consolidation!$H$2:$H$3000="master")*Consolidation!$L$2:$L$3000))/10000'
    sprint_df['Ratio'] = '=Round(INDIRECT("F" &ROW())/INDIRECT("H" &ROW()),2)'
        
    return sprint_df

    
def dataCleansing(temp):
    temp.drop(unwantedColumns, axis = 1, inplace=True, errors='ignore')    
    nunique = find_columns_having_same_value_in_all_row(temp)
    cols_to_drop = nunique[nunique == 1].index
    temp.drop(cols_to_drop, axis=1, inplace=True)
    for col in temp.columns:
        if (temp[col].astype(str).str.contains('https://github.ibm.com/api/v3/').any()): 
            if (temp[col].astype(str).str.contains('anviswa1/melco-ec/statuses').any() == False):  
                if (temp[col].astype(str).str.contains('/anviswa1/melco-ec/pulls').any() == False):
                    temp.drop([col], axis=1, inplace=True)  
          
    return temp


def extract_pr():
    os.system(command_to_extract_pr)  
    jsonFile = open(basePath + pathSeparator + pr_FileName + jsonExtension, 'r', encoding="utf8")
    contents = list(iterparse(jsonFile.read())) #Get all JSON as List i.e. handling ][{
    dfs = [] 
    for i in range(0, len(contents)):   
        data = pd.json_normalize(contents[i]) #normalize individual JSON
        dfs.append(data) 
        
    temp = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.
    temp = dataCleansing(temp)

    return temp
    

def extract_pr_files(pr_df):
    dfs = []
    for i in range (0, len(pr_df)):
        pullNumber = pr_df.iloc[i].number
        #print('pullNumber: ' + str(pullNumber))
        command = base_command + 'pulls/' + str(pullNumber) + '/files  > ' + str(pullNumber)  + jsonExtension
        os.system(command)
        jsonFile = open(basePath + pathSeparator + str(pullNumber) + jsonExtension, 'r', encoding="utf8")
        contents = list(iterparse(jsonFile.read())) #Get all JSON as List i.e. handling ][{   
        for j in range(0, len(contents)):    
            data = pd.json_normalize(contents[j]) #normalize individual JSON
            data.insert(0,'PR_Number', pullNumber)
            #print(f'Data------------------------------------------{len(data)}')
            dfs.append(data)
       
    temp = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.
    temp = dataCleansing(temp)
    temp['extension'] = temp.filename.apply(lambda x: pathlib.Path(x).suffix[1:])
    return temp

    
def extract_pr_comments():
    os.system(command_to_extract_pr_comments)  
    jsonFile = open(basePath + pathSeparator + pr_Comment_FileName + jsonExtension, 'r', encoding="utf8")
    contents = list(iterparse(jsonFile.read())) #Get all JSON as List i.e. handling ][{
    dfs = [] 
    for i in range(0, len(contents)):    
        data = pd.json_normalize(contents[i]) #normalize individual JSON
        data.insert(0,'PR_Number', data['pull_request_url'].str.split('/',).str[-1])
        data['PR_Number'] = (data['PR_Number'] !='n').astype(int)
        dfs.append(data) 
        
    temp = pd.concat(dfs, ignore_index=True) # concatenate all the data frames in the list.
    temp = dataCleansing(temp)
    return temp


def create_consolidated_df(pr_df, pr_files_df, pr_comments_df, extension_df):
    final_dfs = pd.DataFrame()
    final_dfs['PR_Number'] = pd.DataFrame(pr_df['number'])
    final_dfs['UserName'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['user.login']) 
    final_dfs['UserId'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['user.id']) 
    final_dfs['title'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['title'])
    final_dfs['Merged_On'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['merged_at'])
    final_dfs['Merged_On'] = pd.to_datetime( final_dfs ['Merged_On'], errors='coerce', utc=True).dt.strftime('%d-%m-%Y')
    final_dfs['head_ref'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['head.ref'])
    final_dfs['base_ref'] = pr_df['number'].map(pr_df.set_index('number').to_dict()['base.ref'])
    
    for ind1 in final_dfs.index:
        try:
            matched_head_sha = pr_files_df[pr_files_df['PR_Number'] == (final_dfs['PR_Number'][ind1])]
            matched_extn = matched_head_sha.merge(extension_df, on=['extension'], how='left')
            final_dfs.at[ind1, 'Total_Files_Modified'] = len(matched_extn[matched_extn['consideration'] == 'Yes'])
            final_dfs.loc[ind1, 'Lines_Added'] = matched_extn.loc[matched_extn['consideration'].eq('Yes'), 'additions'].sum()
            final_dfs.loc[ind1, 'Lines_Deleted'] = matched_extn.loc[matched_extn['consideration'].eq('Yes'), 'deletions'].sum()
        except Exception as e: 
            print(traceback.format_exc())
            sys.exit(1)
            
    final_dfs ['Effective_Change']  = np.where(final_dfs['Lines_Added'] >= final_dfs['Lines_Deleted'], final_dfs['Lines_Added'] - final_dfs['Lines_Deleted'],final_dfs['Lines_Added'])
    
    for ind1 in final_dfs.index:
        final_dfs.loc[ind1, 'Reviewer_Comment_Count'] = pr_comments_df[(pr_comments_df['pull_request_url'] == (pr_base_link + str(final_dfs['PR_Number'][ind1]))) & (pr_comments_df['in_reply_to_id'].isnull())]['pull_request_url'].count()
        final_dfs.loc[ind1, 'Reviewee_Comment_Count'] = pr_comments_df[(pr_comments_df['pull_request_url'] == (pr_base_link + str(final_dfs['PR_Number'][ind1]))) & (pr_comments_df['in_reply_to_id'].notnull())]['pull_request_url'].count()
    
    return final_dfs

def main():
    pr_df = extract_pr()
    pr_df.dropna(how='all', axis = 1, inplace=True) #axis 0 is column wise and 1 is row wise
    #print(pr_df)
    
    extension_df = create_extension_df()
    #print(extension_df)
    #'''
    pr_files_df = extract_pr_files(pr_df)
    pr_files_df.dropna(how='all', axis='columns')
    #print(pr_files_df)
    pr_comments_df = extract_pr_comments()
    pr_comments_df.dropna(how='all', axis='columns')
    #print(pr_comments_df)
    final_dfs = create_consolidated_df(pr_df, pr_files_df, pr_comments_df, extension_df)
    #print(final_dfs)
   
    summary_dfs = pd.DataFrame()
    summary_dfs = create_sprint_df()
    #'''
    
    writer = pd.ExcelWriter("PR_Analysis_" + dt_string + excelExtension,  engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}})
    
    #'''
    #print(summary_dfs)
    final_dfs.to_excel(writer, sheet_name='Consolidation')
    #'''
    
    pr_df.to_excel(writer, sheet_name='PR')
    
    
    #'''
    pr_comments_df.to_excel(writer, sheet_name='PR_Comments')
    pr_files_df.to_excel(writer, sheet_name='PR_Files')
    summary_dfs.to_excel(writer, sheet_name='Summary')
    
    resize_column(pr_df, 'PR', writer)
    resize_column(pr_comments_df,'PR_Comments', writer)
    resize_column(pr_files_df, 'PR_Files', writer)
    resize_column(final_dfs, 'Consolidation', writer)
    #'''    
    writer.save()
    
    
if __name__ == "__main__":
    main()
