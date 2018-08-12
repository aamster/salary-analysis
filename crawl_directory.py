from selenium import webdriver
import pandas as pd
import random
import time

df = pd.read_csv('SalaryTravel.csv')

def get_professors():
    return df[df.Title.str.contains('PROFESSOR')]

df = get_professors()

browser = webdriver.Chrome()

class MultipleDirectoryMatchesException(Exception):
    pass

class NoDirectoryMatchesException(Exception):
    pass

def submit_form(first_name, last_name):
    first_name_textbox = browser.find_element_by_id('edit-firstname')
    first_name_textbox.send_keys(first_name)

    last_name_textbox = browser.find_element_by_id('edit-lastname')
    last_name_textbox.send_keys(last_name)

    captcha_answer = (browser.find_element_by_name('captcha-answer')
        .get_attribute('value'))
    captcha_textbox = browser.find_element_by_id('edit-captcha-test')
    captcha_textbox.send_keys(captcha_answer)

    captcha_textbox.submit()

def click_detail_link():
    a_tags = browser.find_elements_by_tag_name('a')
    a_tags = [a for a in a_tags if a.get_attribute('href')]
    detail_links = [a for a in a_tags if '/directory/detail' in a.get_attribute('href')]
    if len(detail_links) > 1:
        raise MultipleDirectoryMatchesException()
    elif not detail_links:
        raise NoDirectoryMatchesException()

    detail_link = detail_links[0]
    detail_link.click()

def get_details():
    details = browser.find_elements_by_css_selector('#block-system-main div p')
    detail_text = [d.text for d in details]
    department_raw = detail_text[1]
    title_raw = detail_text[2]

    department = department_raw.split(':')[1].strip()
    title = title_raw.split(':')[1].strip()

    return department, title

def get_first_last_name(name):

    def get_name_parts(name):
        return name.split(',') if ',' in name else (None, None)

    def get_first_name(name):
        last, first = get_name_parts(name)
        return first

    def get_last_name(name):
        last, first = get_name_parts(name)
        return last

    first_name = get_first_name(name)
    last_name = get_last_name(name)

    return first_name, last_name

def crawl():
    details = []

    browser.get('https://www.directory.gatech.edu/')

    for row in df.itertuples():
        first_name, last_name = get_first_last_name(row.Name)
        submit_form(first_name, last_name)

        multiple_matches = False
        try:
            click_detail_link()
            department, title = get_details()
        except MultipleDirectoryMatchesException:
            department, title = None, None
            multiple_matches = True
        except NoDirectoryMatchesException:
            department, title = None, None
        except:
            department, title = None, None
        details.append({
            'Name': row.Name,
            'Department': department,
            'Title': title,
            'MultipleMatches': multiple_matches
        })

        time.sleep(random.randrange(3, 10))

    browser.close()

    return details

if __name__ == '__main__':
    details = crawl()
    details = pd.DataFrame(details)
    details.to_csv('Details.csv', index=False)
