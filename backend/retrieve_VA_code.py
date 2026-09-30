# RETRIEVING CSV and NORMAL CHAPTERS

import requests

import csv

import io

from bs4 import BeautifulSoup

from backend.database import SessionLocal
from backend.models import VirginiaCodeSection

def retrieve_VA_code(sectionNumber):

    requestUrl = f"https://law.lis.virginia.gov/api/CoVSectionsGetSectionDetailsJson/{sectionNumber}"

    # requests.get() means using the imported library, send an HTTP GET request to the requestUrl vairable
    response = requests.get(requestUrl)

    # responseData is the entire HTTP response object
    # whole thing is saying take the JSON contained in the response body and convert it into normal python data
    responseData = response.json()

    sectionData = responseData["ChapterList"][0]

    sectionBody = sectionData["Body"]

    # take the HTML VA gave us and interpret the <p> as HTML structure, rather than treating those tags as statute text
    sectionHTML = BeautifulSoup(sectionBody, "html.parser")

    # .get_text() means give me the text inside those HTML elements
    sectionText = sectionHTML.get_text(separator="\n", strip=True)

    return sectionText


def retrieve_VA_code_chapters(titleNumber):

    chaptersUrl = f"https://law.lis.virginia.gov/api/CoVChaptersGetListOfJson/{titleNumber}"

    chaptersResponse = requests.get(chaptersUrl)

    chaptersData = chaptersResponse.json()

    return chaptersData


def retrieve_VA_code_csv(titleNumber):

    csvUrl = f"https://law.lis.virginia.gov/CSV/CoVTitle_{titleNumber}.csv"

    csvResponse = requests.get(csvUrl)

    csvFile = io.StringIO(csvResponse.text)

    # DictReader turns the ugly style text into formatted and readable rows
    csvData = csv.DictReader(csvFile)

    return csvData


def retrieve_VA_code_sections(titleNumber, chapterNumber):

    sectionsUrl = f"https://law.lis.virginia.gov/api/CoVSectionsGetListOfJson/{titleNumber}/{chapterNumber}"

    sectionsResponse = requests.get(sectionsUrl)

    sectionsData = sectionsResponse.json()

    return sectionsData

if __name__ == "__main__":

    titlesUrl = "https://law.lis.virginia.gov/api/CoVTitlesGetListOfJson"

    titlesResponse = requests.get(titlesUrl)

    titlesData = titlesResponse.json()

    virginiaCodeCatalog = []

    # loop through every title in the code of VA
    for title in titlesData:

        titleNumber = title["TitleNumber"]

        chaptersData = retrieve_VA_code_chapters(titleNumber)

        # loop through every chapter inside the current title
        for chapter in chaptersData["ChapterList"]:

            chapterNumber = chapter["ChapterNum"]

            if not chapterNumber:

                fallbackSections = retrieve_VA_code_csv(titleNumber)

                for section in fallbackSections:

                    virginiaCodeCatalog.append({

                        "sectionNumber": section["Section"],
                        "sectionTitle": section["Title"]
                    })

                # continue on to the next line instead of making normal REST request
                continue

            sectionsData = retrieve_VA_code_sections(titleNumber, chapterNumber)

            # loop through every article inside the current chapter
            for article in sectionsData["ArticleList"]:

                for subPart in article["SubPartList"]:

                    for section in subPart["SectionList"]:

                        virginiaCodeCatalog.append({

                            "sectionNumber": section["SectionNumber"],
                            "sectionTitle": section["SectionTitle"]
                        })

    print("Sections Loaded:", len(virginiaCodeCatalog))


    db = SessionLocal()

    # keeps track of section numbers already added
    savedSectionNumbers = set()

    # loop through every VA Code section collected
    for section in virginiaCodeCatalog:

        # get the section number for the current section
        sectionNumber = section["sectionNumber"]

        # if we've already seen this section number, skip this duplicate
        if sectionNumber in savedSectionNumbers:
            continue

        # remember this section number
        savedSectionNumbers.add(sectionNumber)

        # create a db row from this section
        code_section_row = VirginiaCodeSection(
            section_number=sectionNumber,
            section_title_and_description=section["sectionTitle"]
        )

        # queue this row to be inserted into PostgreSQL
        db.add(code_section_row)

    db.commit()
    db.close()