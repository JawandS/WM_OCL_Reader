# imports
from bs4 import BeautifulSoup as bs
import urllib.request
import os

dir_path = os.getcwd()
homepage = "https://courselist.wm.edu/courselist/courseinfo/"

# go through and get all of the subjects 
def get_course_names():
    # course names
    course_names = []
    # get the html
    fp = urllib.request.urlopen(homepage)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    with open(f"{dir_path}\\homepage.html", "w") as f:
        f.write(mystr)
    fp.close()
    # read in the homepage html into beautiful soup
    with open(f"{dir_path}\\homepage.html", "r") as f:
        soup = bs(f.read(), "html.parser")
        # get all of the option values inside the term_subj select
        options = soup.find("select", {"name": "term_subj"}).find_all("option")
        # get the course names from options
        for option in options:
            course_names.append(option.get("value"))
    # remove ALL from course_names
    if "0" in course_names:
        course_names.remove("0")
    # return
    return course_names

# go through each course code and get all open courses
def get_courses(course_code):
    page_url = f"https://courselist.wm.edu/courselist/courseinfo/searchresults?term_code=202420&term_subj={course_code}&attr=0&attr2=0&levl=0&status=OPEN&ptrm=0&search=Search"
    # get the html
    fp = urllib.request.urlopen(page_url)
    mybytes = fp.read() 
    html_data = mybytes.decode("utf8")
    fp.close()
    # read into beautiful soup
    soup = bs(html_data, "html.parser")
    table = soup.find("table")
    with open(f"{dir_path}\\data.csv", "a") as f:
        # collect data
        for column in table.tbody.find_all('td'):
            # if the column is a link start a new rwo in the csv
            if column.find("a") != None:
                f.write("\n")
                # get the text from the a
                f.write(f"{column.find('a').text},")
            else: # standard text
                to_write = column.text
                if not to_write:
                    to_write = ""
                f.write(f"{to_write.strip()},")

def main():
    # get the course codes
    course_codes = ['AFST', 'AMST', 'ANTH', 'APSC', 'ARAB', 'ART', 'ARTH', 'AMES', 'APIA', 'BIOL', 'BUAD', 'CHEM', 'CHIN', 'CLCV', 'COLL', 'CMST', 'CAMS', 'CSCI', 'CONS', 'CRWR', 'CRIN', 'DANC', 'DATA', 'ECON', 'EPPL', 'EDUC', 'ELEM', 'EPAD', 'ENGL', 'ENSP', 'EURS', 'FMST', 'FREN', 'GSWS', 'GIS', 'GEOL', 'GRMN', 'GBST', 'GOVT', 'GRAD', 'GREK', 'HSCI', 'HBRW', 'HISP', 'HIST', 'INTR', 'INRL', 'ITAL', 'JAPN', 'KINE', 'LATN', 'LAS', 'LAW', 'LING', 'MSCI', 'MATH', 'MREN', 'MLSC', 'MDLL', 'MUSC', 'NSCI', 'PHIL', 'PHYS', 'PSYC', 'PBHL', 'PUBP', 'RELG', 'RUSN', 'RPSS', 'SOCL', 'SPCH', 'THEA', 'WRIT']
    # create the data csv
    with open(f"{dir_path}\\data.csv", "w") as f:
        f.write("CRN,COURSE ID,CRSE ATTR,TITLE,INSTRUCTOR,CRDT HRS,MEET DAY:TIME,PROJ ENR,CURR ENR,SEATS AVAIL,STATUS")
    # go through each course code and add all open courses to the csv
    for code in course_codes:
        get_courses(code)

# main method
if __name__ == "__main__":
    main()
    