import logging as log
from dotenv import dotenv_values
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

class SurveyTaker:
    def __init__(self, website, browser, headless=True, verbose=False):
        driver = None

        # handle browser choice
        if browser == 'firefox':
            # handle headless arg
            if headless:
                options = webdriver.FirefoxOptions()
                options.add_argument('-headless')
                driver = webdriver.Firefox(options=options)
            else:
                driver = webdriver.Firefox()
        elif browser == 'chrome':
            if headless:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                driver = webdriver.Chrome(options=options)
            else:
                driver = webdriver.Chrome()

        # navigate to site
        driver.get(website)
        self.driver = driver
        self.website = website
        self.verbose = verbose
        self.nextId = 'nextButton'  # may need to be overriden by subclasses

    # Presses the next button on page
    def next(self, times=1):
        for _ in range(times):
            log.info('Clicking next button on page')
            nextButton = self.driver.find_element(By.ID, self.nextId)
            nextButton.click()

    # Types text into a specified field
    def type(self, method, key, text):
        log.info(
            f'Typing "{text}" into element with key {key}, of type {method}')
        textField = self.driver.find_element(method, key)
        textField.send_keys(text)

    # Clicks a button, or multiple
    def click(self, method, key):
        log.info(
            f'Clicking element with key {key}, of type {method}')
        buttons = self.driver.find_elements(method, key)
        for b in buttons:
            b.click()

    # Selects an option in a dropdown menu
    def select_option(self, method, key, value):
        selector = Select(self.driver.find_element(method, key))
        selector.select_by_value(value)

    # Takes entire survey. To be implemented by subclasses
    def survey(self):
        pass


class HomeDepotSurveyTaker(SurveyTaker):
    keys = {
        'begin': (By.ID, 'beginButton'),
        'zip': (By.NAME, 'spl_q_thd_postalcode_entry_text'),
        'userId': (By.NAME, 'spl_q_thd_receiptcode_id_entry_text'),
        'pw': (By.NAME, 'spl_q_thd_receiptcode_password_entry_text'),
        'contracting': (By.ID, 'i_onf_q_thd_pro_classification_contractor_remodeling_yn_1'),
        'building': (By.ID, 'i_onf_q_thd_pro_classification_contractor_building_construction_yn_1'),
        'highRating': (By.CLASS_NAME, 'cell-5'),
        'shopExperience': (By.ID, 'spl_q_thd_shop_experience_text_input'),
        'employeeGreet': (By.ID, 'i_onf_q_thd_get_employee_greeting_yn_1'),
        'addressNeeds': (By.ID, 'i_onf_q_thd_get_employee_interest_addressing_needs_yn_1'),
        'thanked': (By.ID, 'i_onf_q_thd_get_employee_thanked_you_yn_1'),
        'noSpecial': (By.ID, 'i_onf_q_thd_praise_employee_yn_2'),
        'optOut': (By.ID, 'i_onf_q_thd_catchall_oe_optout_yn_1'),
        'frustrations': (By.ID, 'spl_i_question_1_input'),
        'indifferent': (By.ID, 'i_onf_i_question_1_3'),
        'noHelp': (By.ID, 'i_onf_i_question_2_4'),
        'FIRSTNAME': (By.NAME, 'spl_q_thd_contact_first_name_text'),
        'LASTNAME': (By.NAME, 'spl_q_thd_contact_last_name_text'),
        'EMAIL': (By.NAME, 'spl_q_thd_contact_email_sweeps_text'),
        'PHONE': (By.NAME, 'spl_q_thd_contact_phone_sweeps_text'),
        'finish': (By.ID, 'finishButton')
    }

    def __init__(self, browser, headless=True, verbose=False):
        super().__init__('https://homedepot.com/survey', browser, headless, verbose)

        self._uniqueQuestions = [
            'On this visit, did an employee make your visit great by doing something special or provide service that was “above and beyond” your expectations?'
        ]

    # Take a survey. Expects the following values:
    # user: username
    # pw: password
    # pinfo: personal info in table
    def survey(self, user, pw, pinfo):
        keys = HomeDepotSurveyTaker.keys
        # begin survey
        self.click(*keys['begin'])

        # fill in zipcode
        self.type(*keys['zip'], pinfo['ZIP'])
        self.next(2)

        # fill in username and password
        self.type(*keys['userId'], user)
        self.type(*keys['pw'], pw)
        self.next()

        # check for error in inputting user/pw
        # if valid credentials entered, pass will be reached
        try:
            self.type(*keys['userId'], 'test ID')
            log.error('Invalid credentials specified, terminating survey')
            self.driver.quit()
            return True
        except Exception:
            pass

        # select general contracting/remodeling and building/construction
        self.click(*keys['contracting'])
        self.click(*keys['building'])
        self.next()

        # select definitely will to shop at home depot again
        # also select much better for shopping experience compared to other stores
        for _ in range(2):
            self.click(*keys['highRating'])
            self.next()

        # fill in textbox with something
        responses = [
            'My checkout time was very fast.',
            'The employees were very friendly.',
            'The store had everything I needed in stock.',
            'The store was very clean.',
            'The employees helped me find what I was looking for.',
        ]
        self.type(*keys['shopExperience'], choice(responses))
        self.next()

        # select extremely satisfied for both questions for each visit
        # also select strongly agree for all answers
        for _ in range(2):
            self.click(*keys['highRating'])
            self.next()

        # select yes for all 3 questions
        self.click(*keys['employeeGreet'])
        self.click(*keys['addressNeeds'])
        self.click(*keys['thanked'])
        self.next()

        # prepare scenarios for questions
        question = self.driver.find_element(By.CLASS_NAME, 'question')
        questionContent = question.text
        if questionContent == self._uniqueQuestions[0]:
            self.click(*keys['noSpecial'])
        else:
            # TODO: add better handling for unknown questions
            log('warn', 'No code present for this question! Fill it out manually and continue!')
            input()
        self.next()

        # do not share anything else
        self.click(*keys['optOut'])
        self.next()

        # include a check for frustrations question
        try:
            self.type(*keys['frustrations'], 'No frustrations to share.')
            self.next()
        except Exception:
            pass

        # include a check for checkout question, potentially rewrite to look for alternative questions
        try:
            self.click(*keys['indifferent'])
            self.click(*keys['noHelp'])
            self.next()
        except Exception:
            pass

        # fill out sweepstakes info
        for field in ['FIRSTNAME', 'LASTNAME', 'EMAIL', 'PHONE']:
            self.type(*keys[field], pinfo[field])

        # finish
        self.click(*keys['finish'])

        print('Congratulations! Survey submitted successfully!')
        print('Press enter to continue.')
        input()
        self.driver.quit()
        return True


class TropicalSurveyTaker(SurveyTaker):
    keys = {
        'storeNum': (By.ID, 'InputStoreNum'),
        'date': (By.ID, 'Index_VisitDateDatePicker'),
        'hour': (By.ID, 'InputHour'),
        'minute': (By.ID, 'InputMinute'),
        'meridian': (By.ID, 'InputMeridian'),
        'transactNum': (By.ID, 'InputTransactionNum'),
        '2': (By.CLASS_NAME, 'Opt2'),
        '5': (By.CLASS_NAME, 'Opt5'),
        '9': (By.CLASS_NAME, 'Opt9'),
        'carryOut': (By.XPATH, '//label[@for="R000006.2"]'),
        'atRestaurant': (By.XPATH, '//label[@for="R000102.2"]'),
        'smoothie': (By.XPATH, '//label[@for="R000007.2"]'),
        'response': (By.ID, 'S000058'),
        'bahama': (By.XPATH, '//label[text()="Bahama Mama"]'),
        'menuRec': (By.XPATH, '//td[@aria-labelledby="textR000024" and contains(@class, "Opt2")]'),
        'greeted': (By.XPATH, '//td[@aria-labelledby="textR000021" and contains(@class, "Opt1")]'),
        'repeated': (By.XPATH, '//td[@aria-labelledby="textR000026" and contains(@class, "Opt1")]'),
        'app': (By.XPATH, '//td[@aria-labelledby="textR000070" and contains(@class, "Opt2")]'),
        'thanked': (By.XPATH, '//td[@aria-labelledby="textR000027" and contains(@class, "Opt1")]'),
        'supplement': (By.XPATH, '//td[@aria-labelledby="textR000019" and contains(@class, "Opt2")]'),
        'fourOrMore': (By.XPATH, '//label[@for="R000060.4"]'),
        'code': (By.CLASS_NAME, 'ValCode')
    }

    def __init__(self, browser, headless=True, verbose=False):
        super().__init__('https://tsclistens.com', browser, headless, verbose)
        self.nextId = 'NextButton'

    # Takes the survey. Expects the following values in valid formats:
    # storeNum: store number
    # date: date (in MM/DD/YYYY format)
    # time: time (in HH:MM AM/PM format)
    # transactNum: transaction number
    def survey(self, storeNum, date, time, transactNum):
        keys = TropicalSurveyTaker.keys
        # fill in starting page information
        self.type(*keys['storeNum'], storeNum)

        # date entry box is readonly since the website
        # wants you to use a date selector
        # easily overriden by removing readonly attrib
        dateElem = self.driver.find_element(*keys['date'])
        self.driver.execute_script(
            'arguments[0].removeAttribute("readonly")', dateElem)
        self.type(*keys['date'], date)

        # have to select three individual select boxes for time input
        hour = time[0:2]
        minute = time[3:5]
        meridian = time[6:]
        self.select_option(*keys['hour'], hour)
        self.select_option(*keys['minute'], minute)
        self.select_option(*keys['meridian'], meridian)

        self.type(*keys['transactNum'], transactNum[-4:])
        self.next()

        # check for error in inputting store number again
        # if valid credentials entered, pass will be reached
        try:
            test = self.type(*keys['storeNum'], 'test value')
            log.error('Invalid credentials specified, terminating survey')
            self.driver.quit()
            return True
        except Exception:
            pass

        # select highly satisfied
        self.click(*keys['5'])
        self.next()

        # select carry out
        self.click(*keys['carryOut'])
        self.next()

        # select at the restaurant
        self.click(*keys['atRestaurant'])
        self.next()

        # select smoothie only
        self.click(*keys['smoothie'])
        self.next()

        # select highly satisfied with all, and N/A response for menu knowledge
        self.click(*keys['5'])
        self.click(*keys['9'])  # N/A response
        self.next()

        # select highly satisfied with all again
        self.click(*keys['5'])
        self.next()

        # select no problem w/experience
        self.click(*keys['2'])
        self.next()

        # select highly satisfied with all again
        self.click(*keys['5'])
        self.next()

        # input textbox
        # TODO: add code to generate generic response
        text = input(
            'Supply some feedback text: ')
        self.type(*keys['response'], text)
        self.next()

        # select bahama mama
        self.click(*keys['bahama'])
        self.next()

        # select no to recognize staff member
        self.click(*keys['2'])
        self.next()

        # select the following:
        # no to menu recs,
        # yes to being greeted,
        # yes to repeat order,
        # no to telling about app
        # no to added supplement
        # yes to thanked
        # questions may be scrambled, so attempting to select them all and then going to the next page to answer remaining
        for i in range(3):
            for q in ['menuRec', 'greeted', 'repeated', 'app', 'thanked', 'supplement', 'fourOrMore']:
                try:
                    self.select(*keys[q])
                except:
                    pass
            self.next()

        # select four or more visits in past 30 days
        # self.click(*keys['fourOrMore'])
        # self.next()

        # select no to all
        self.click(*keys['2'])
        self.next()

        # extract validation code
        codeElem = self.driver.find_element(*keys['code'])
        print('Congratulations! Survey submitted successfully!')
        print(f'Your code is {codeElem.text[-5:]}.')
        print('Press enter to continue.')
        input()
        self.driver.quit()
        return True


if __name__ == '__main__':
    print('This program is a module. Import it in a script!')
