import logging as log
from dotenv import dotenv_values
from libsurvey import HomeDepotSurveyTaker, TropicalSurveyTaker
from argparse import ArgumentParser

pinfoValues = dotenv_values('.env')

def main(args):
    if args.verbose:
        log.basicConfig(format='[%(levelname)s] %(message)s', level=log.INFO)
    else:
        log.basicConfig(format='[%(levelname)s] %(message)s', level=log.WARNING)
        #log.basicConfig(format='[%(levelname)s] %(message)s', level=log.INFO)

    print('[1] Home Depot')
    print('[2] Tropical Smoothie Cafe')
    choice = input('Please select a survey type to take (or q to quit): ')
    if choice == '1':
        user = input('Please type the user ID on your receipt (or q to quit): ')
        if user.lower() == 'q':
            print('Quitting!')
            return False
        pw = input('Please type the password on your receipt: ')
        print('Performing survey...')
        hdSurvey = HomeDepotSurveyTaker(args.browser, not args.noheadless, args.verbose)
        return hdSurvey.survey(user, pw, pinfoValues)
    elif choice == '2':
        storeNum = input('Please type the store number: ')

        def validDate(date):
            if len(date) != 10 or len(date.split('/')) != 3:
                return False
            try:
                if int(date[0:2]) not in range(1,13):
                    return False
                if int(date[3:5]) not in range(1,32):
                    return False
                year = int(date[6:])
            except:
                return False
            
            return True

        date = input('Please type the date on the receipt (in MM/DD/YYYY format): ')
        while not validDate(date):
            print('Invalid date format!')
            date = input('Please type the date on the receipt (in MM/DD/YYYY format): ')

        def validTime(time):
            if len(time) != 8 or len(time.split(' ')) != 2:
                return False
            try:
                if int(time[0:2]) not in range(1,13):
                    return False
                if int(time[3:5]) not in range(0,61):
                    return False
                if time[6:] != 'AM' and time[6:] != 'PM':
                    return False
            except:
                log.debug('An exception occurred in determining a valid time')
                return False
            return True

        time = input('Please type the time on the receipt (in HH:MM AM/PM format): ')
        while not validTime(time):
            print('Invalid time format!')
            time = input('Please type the time on the receipt (in HH:MM AM/PM format): ')

        transactId = input('Please type your order/transaction ID (or the last 4 digits of it): ')
        tropicalSurvey = TropicalSurveyTaker(args.browser, not args.noheadless, args.verbose)
        return tropicalSurvey.survey(storeNum, date, time, transactId)

    elif choice == 'q':
        print('Quitting!')
        return False

    else:
        print('Invalid choice!')
        return True

parser = ArgumentParser()
parser.add_argument('-b', dest='browser', choices=['firefox', 'chrome'], required=True, help='Browser to use for survey')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose/debug output toggle')
parser.add_argument('-nh', '--noheadless', action='store_true', help='Run program with visible browser')

args = parser.parse_args()

while main(args):
    pass 
