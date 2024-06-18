from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import json

COMPANY_NAME_CLASS = "company-name hover:underline"
BATCH_NAME_CLASS = "ml-2 text-sm text-gray-400"
COMPANY_IMAGE_CLASS = "mt-2 sm:w-28"
BYLINE_NAME_CLASS = "mt-3 text-gray-700"
TAGS_CLASS = "detail-label text-sm"
JOB_LINKS_CLASS = "rounded-md bg-brand p-2 text-white hover:bg-brand-600"
COMPANY_LINKS_CLASS = "text-blue-600 ellipsis"

FOUNDER_NAME_CLASS = "mb-1 font-medium"
FOUNDER_IMAGE_CLASS = "ml-2 mr-2 h-20 w-20 rounded-full sm:ml-5"
FOUNDER_DESCRIPTION_CLASS = "sm:text-md w-full text-sm"
FOUNDER_LINKEDIN_CLASS = "fa fa-linkedin ml-4 p-1 text-blue-600"

JOB_TITLE_CLASS = "company-name text-2xl font-bold"
SALARY_RANGE_CLASS = "text-gray-500 my-2"
JOB_TAGS_CLASS_1 = (
    "text-gray-500 border border-gray-300 flex p-1 rounded-md text-sm mt-2 mr-2"
)
JOB_TAGS_CLASS_2 = (
    "text-gray-500 border border-gray-300 flex p-1 rounded-md text-sm mt-2"
)
JOB_DESCRIPTION_CLASS = "prose max-w-none prose-p:mb-2"


############
# Replace this URL
url = "https://www.workatastartup.com/companies/leafpress"
############

# should have a defined schema / Pydantic model for generalization
company_data = {
    "name": "",
    "url": "",
    "batch": "",
    "company_image": "",
    "byline": "",
    "tags": [],
    "job_links": [],
    "founders": [],
    "jobs": [],
}

company_data["url"] = url

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
chrome_service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
driver.implicitly_wait(15)

driver.get(url)
page_source = driver.page_source

soup = BeautifulSoup(page_source, "html.parser")


def element_attribute(soup, selector, attribute):
    try:
        elt = soup.find(class_=selector)
        if elt:
            return elt.get(attribute, None)
        else:
            return None
    except:
        return None


def element_attributes(soup, selector, attribute):
    try:
        elts = soup.find_all(class_=selector)
        if elts:
            return [elt.get(attribute, None) for elt in elts]
        else:
            return None
    except:
        return None


def element_text(soup, selector):
    try:
        elt = soup.find(class_=selector)
        if elt:
            return elt.text.strip()
        else:
            return None
    except:
        return None


def element_texts(soup, selector):
    try:
        elts = soup.find_all(class_=selector)
        if elts:
            return [elt.text.strip() for elt in elts]
        else:
            return None
    except:
        return None


def founder_data():
    founder_names = element_texts(soup, FOUNDER_NAME_CLASS)
    founder_images = element_attributes(soup, FOUNDER_IMAGE_CLASS, "src")
    founder_descriptions = element_texts(soup, FOUNDER_DESCRIPTION_CLASS)
    founder_linkedins = element_attributes(soup, FOUNDER_LINKEDIN_CLASS, "href")

    founders = []
    for name, image, description, linkedin in zip(
        founder_names, founder_images, founder_descriptions, founder_linkedins
    ):
        founder = {
            "founder_name": name,
            "founder_image": image,
            "founder_description": description,
            "founder_linkedin": linkedin,
        }
        founders.append(founder)

    return founders


def job_data(job_url):
    if not job_url:
        return None

    driver.get(job_url)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    job_soup = BeautifulSoup(driver.page_source, "html.parser")

    job_title = element_text(job_soup, JOB_TITLE_CLASS)
    salary_range = element_text(job_soup, SALARY_RANGE_CLASS)

    tag_list_1 = element_texts(job_soup, JOB_TAGS_CLASS_1)
    tag_list_2 = element_texts(job_soup, JOB_TAGS_CLASS_2)
    if tag_list_1 and tag_list_2:
        job_tags = tag_list_1 + tag_list_2
    elif tag_list_1:
        job_tags = tag_list_1
    elif tag_list_2:
        job_tags = tag_list_2
    else:
        job_tags = None

    job_description = element_texts(job_soup, JOB_DESCRIPTION_CLASS)[1]

    job = {
        "job_url": job_url,
        "job_title": job_title,
        "salary_range": salary_range,
        "job_tags": job_tags,
        "job_description": job_description,
    }

    return job


company_data["name"] = element_text(soup, COMPANY_NAME_CLASS)
company_data["batch"] = element_text(soup, BATCH_NAME_CLASS)
company_data["company_image"] = element_attribute(soup, COMPANY_IMAGE_CLASS, "src")
company_data["byline"] = element_text(soup, BYLINE_NAME_CLASS)
company_data["tags"] = element_texts(soup, TAGS_CLASS)
company_data["job_links"] = element_attributes(soup, JOB_LINKS_CLASS, "href")
company_data["founders"] = founder_data()
company_data["jobs"] = [job_data(job_url) for job_url in company_data["job_links"]]

driver.quit()

with open("data.json", "w") as f:
    json.dump(company_data, f, indent=2, ensure_ascii=False)
