# keep track of courses and alert the user if they go from open to close

# imports
import pandas as pd
from ocl_downloader import main as update_courselist # update the courslist (data.csv)
import os 

UPDATE_COURSELIST_FLAG = False

def main():
    # update the courslist
    if UPDATE_COURSELIST_FLAG:
        update_courselist()
    # get the courslist
    courselist = pd.read_csv("data.csv", encoding='latin-1')
    # get the tracked courses from the last time the program was run
    tracked_courses = pd.read_csv("tracking.csv")
    # go through courses and build courses that need to be updated
    courses_to_update_user = []
    for crn, row in tracked_courses.iterrows():
        print(len(all_crn))
        print(crn in all_crn)
        prev_course_status = row["status"] # course status from last run
        # get the row of the course from the courselist
        course_row = courselist.loc[courselist["CRN"] == crn]
        # check course status
        course_status = course_row["STATUS"].values[0]
        # check if the course status is different
        if course_status != prev_course_status:
            # add course to courses to update
            courses_to_update_user.append(course_row)

    # replace tracked_courses with courses to update
    for course_data in courses_to_update_user:
        # get the course identifier
        tracked_courses.loc[tracked_courses["course"] == course_data["COURSE ID"]]["status"] = course_data["STATUS"]
    # go through courses to update and alert the user
    email = f"Hello User,\n\nThe following courses have changed status:\n{courses_to_update_user}\n\nThank you for using the OCL Tracker!"
    # send email
    print(email)


# main method
if __name__ == "__main__":
    main()