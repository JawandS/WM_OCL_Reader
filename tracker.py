# keep track of courses and alert the user if they go from open to close
# using: https://console.cloud.google.com/welcome?project=wm-ocl-reader

# imports
import pandas as pd
from ocl_downloader import main as update_courselist # update the courslist (data.csv)

import json
import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

UPDATE_COURSELIST_FLAG = True

def send_email(email):
    try:
        # Load the credentials from the json file
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # google service
        service = build("gmail", "v1", credentials=creds)
        # create message
        msg = EmailMessage()
        # set the content
        msg.set_content(email)
        # set the subject
        msg['Subject'] = "Course Status Update"
        # get the data from secrets
        with open("secrets.json") as f:
            secrets = json.load(f)
            # set the from
            msg['From'] = secrets["from"]
            # set the to
            msg['To'] = secrets["to"]
        # use the google api to send the message
        encoded_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        create_msg = {"raw": encoded_msg}
        # send the message 
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_msg)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    print(send_message)

def generate_email(courses_to_update_user):
    # go through courses to update and alert the user
    email = f"Hello User,\n\nThe following courses have changed status:\n"
    for course_data in courses_to_update_user:
        course_name = course_data["COURSE ID"]
        crn = course_data["CRN"]
        status = course_data["STATUS"]
        email += f"Course: {course_name} ({crn}) is now {status}\n"
    email += f"\nGenerated at: {pd.Timestamp.now()}"
    return email

def check_for_updates():
    # update the courslist
    if UPDATE_COURSELIST_FLAG:
        update_courselist()
    # get the courslist
    courselist = pd.read_csv("data.csv", encoding='Latin-1', index_col=False)
    # get the tracked courses from the last time the program was run
    tracked_courses = pd.read_csv("tracking.csv", index_col=False)
    # go through courses and build courses that need to be updated
    courses_to_update_user = []
    for index, row in tracked_courses.iterrows():
        prev_course_status = row["status"] # course status from last run
        crn = str(int(row["crn"])) # convert crn to string
        # get the course row from the courselist
        for index, course_row in courselist.iterrows():
            if str(course_row["CRN"]) == crn:
                # check course status
                course_status = course_row["STATUS"]
                # check if the course status is different
                if course_status != prev_course_status:
                    # add course to courses to update
                    courses_to_update_user.append(course_row)
                break
    if not courses_to_update_user:
        print("No courses to update")
        return []
    # replace tracked_courses with courses to update
    for course_data in courses_to_update_user:
        # get the crn
        crn = course_data["CRN"]
        # get the status
        status = course_data["STATUS"]
        # get the index of the row
        index = tracked_courses[tracked_courses["crn"] == crn].index[0]
        # update the status
        tracked_courses.at[index, "status"] = status
        # add the course name
        tracked_courses.at[index, "name"] = course_data["COURSE ID"]
    # write to tracking.csv
    tracked_courses.dropna(how='all', axis=1, inplace=True)
    tracked_courses.to_csv("tracking.csv", index=False)
    # return the courses to update
    return courses_to_update_user

def main():
    # check for updates
    courses_to_update = check_for_updates()
    if len(courses_to_update) > 0:
        # generate email
        email = generate_email(courses_to_update)
        # send email
        send_email(email)


# main method
if __name__ == "__main__":
    main()