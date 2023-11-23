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
    courselist = pd.read_csv("data.csv", encoding='Latin-1', index_col=False)
    # get the tracked courses from the last time the program was run
    tracked_courses = pd.read_csv("tracking.csv", index_col=False)
    # go through courses and build courses that need to be updated
    courses_to_update_user = []
    for index, row in tracked_courses.iterrows():
        prev_course_status = row["status"] # course status from last run
        crn = str(row["crn"]) # convert crn to string
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
    # go through courses to update and alert the user
    email = f"Hello User,\n\nThe following courses have changed status:\n{courses_to_update_user}\n\nThank you for using the OCL Tracker!"
    # send email
    print(email)


# main method
if __name__ == "__main__":
    main()