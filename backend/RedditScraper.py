import re
import os
import sys
import idlelib
import traceback
import subprocess
import string
import praw
import pandas as pd
import datetime as dt
import tkinter as Tkinter
import tkinter.filedialog
tkFileDialog = tkinter.filedialog

class redditscraper():

    def __init__(self):
        self.credentials = self.__Get_Credentials_File__()
        
    def __Get_Credentials_File__(self, credentials_file = 'Credentials.txt'):
    
        txt_file_path = credentials_file

        #Create window for the TXT File Selection
        root = Tkinter.Tk()
        root.withdraw()
        
        if not os.path.isfile(credentials_file):

            # Where Am I File & Path
            file_path = sys._getframe().f_code.co_filename

            # This Directory
            Dir = os.path.dirname(file_path)

            #Abbreviate
            Select_File = tkFileDialog.askopenfilename

            T = "Select File Path to Credentials.txt"
            F = (("TXT files","*.txt"),("all files","*.*"))
            TF = Select_File(initialdir = Dir, title = T, filetypes = F)
        
            txt_file = TF

        CF = open(credentials_file, 'r')
        CF_Data = CF.read()
        CF.close()

        credentials_dictionary = {}
        
        for Line in CF_Data.splitlines():
            if not Line.strip():
                continue

            Key, Value = Line.split('=')

            credentials_dictionary[Key.strip()] = Value.strip()

        return credentials_dictionary

    def __get_date__(self, created):
        return dt.datetime.fromtimestamp(created)

    def Get_Reddit_Comments(self, Sub_Reddit_Topic, Limit):

        YOUR_APP_NAME                = self.credentials['YOUR_APP_NAME']
        PERSONAL_USE_SCRIPT_14_CHARS = self.credentials['PERSONAL_USE_SCRIPT_14_CHARS']
        SECRET_KEY_27_CHARS          = self.credentials['SECRET_KEY_27_CHARS']
        YOUR_REDDIT_USER_NAME        = self.credentials['YOUR_REDDIT_USER_NAME']
        YOUR_REDDIT_LOGIN_PASSWORD   = self.credentials['YOUR_REDDIT_LOGIN_PASSWORD']

        try:

            # Getting a Reddit instance
            Reddit = praw.Reddit(client_id=PERSONAL_USE_SCRIPT_14_CHARS,
                            client_secret=SECRET_KEY_27_CHARS,
                            user_agent=YOUR_APP_NAME, 
                            username=YOUR_REDDIT_USER_NAME, 
                            password=YOUR_REDDIT_LOGIN_PASSWORD)

            # Getting a Sub Reddit instance
            subreddit = Reddit.subreddit(Sub_Reddit_Topic)

            # Let’s just grab the most up-voted topics all-time with:
            # be aware that Reddit’s request limit* is 1000
            top_subreddit = subreddit.comments(limit=Limit) #{sort: 'top', time_filter:'day'})

            topics_dict = { "score":[], 
                        "link_id":[],   
                        "created_utc": [], 
                        "body":[]}

            for submission in top_subreddit:
                print(submission)
                topics_dict["score"].append(submission.score)
                topics_dict["link_id"].append(submission.link_id)
                topics_dict["created_utc"].append(submission.created_utc)
                topics_dict["body"].append(submission.body)
        
            topics_data = pd.DataFrame(topics_dict)
        
            #_timestamp = topics_data["created"].apply(self.__get_date__)
        
            #topics_data = topics_data.assign(timestamp = _timestamp)
        
            # topics_data.to_csv('Sub_Reddit_Topics.csv', index=False)

            return topics_data
        
        except Exception as e:

            print(e)

            if "401" in str(e):

                print('\nWeb Access Error. Invalid or Missing Credentials.\n')
                print('Please update Credentials.txt before using this this API.\n')

            if "400" in str(e) or "403" in str(e)or "404" in str(e):

                Topic = Sub_Reddit_Topic
                print('\nWeb Access Error.\n')
                print('Please check your Sub_Reddit_Topic. --> '+ Topic +'\n')
                print('Server could not understand request due to invalid syntax.')
                print('Suggestions: \nFood \nFitness \nGaming \nTechnology')
                print('Facepalm \nAww\n\n')
                
            input("Press any key to exit . . .")

            sys.exit(0)

    #----------------------------------------------------------------

if __name__ == '__main__':

    RS = redditscraper()
    
    if "'YOUR_REDDIT_LOGIN_PASSWORD': 'PASSWORS'" in repr(RS.credentials):
        print('Credentials.txt needs to be filed out before using this API.\n')
        input("Press any key to exit . . .")
        sys.exit(0)
        
    Topic = 'politics'#input("Type Sub_Reddit_Topic here -->> ")

    print("\n\nBe aware that Reddit’s request limit* is 1000 \n")

    Limit = 200#input("Type the number of Reddit Request here -->> ")
    
    print("\n\nGetting Reddit_Comments . . . \n\n")

    print(RS.Get_Reddit_Comments(Topic, int(Limit)))
    
    input("\n\nSee output csv file Sub_Reddit_Topics.csv'")
