Dedicated to my father.

# Survey Automator
A program that allows the automation of surveys with [Selenium](https://selenium.dev), including a library that can serve as a basic framework to write your own survey automation scripts.

Currently, the program supports surveys for [Home Depot](https://homedepot.com/survey) and [Tropical Smoothie Café](https://tsclistens.com) (unstable).

## Requirements
### Dependencies
* [Python](https://python.org)
* [Selenium](https://selenium.dev)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

You can install the Python dependencies with `pip`:
```
pip install -r requirements.txt
```

### Other Requirements
You will also need a `.env` file in the program's directory containing the fields `ZIP`, `FIRSTNAME`, `LASTNAME`, `EMAIL`, and `PHONE`. These environmental variables are currently used in automating the Home Depot survey to enter the sweepstakes at the end of the survey, which requires this information. A template `.env` file is available in `.env.example`.

## Usage
```console
$ python surveytaker.py -b BROWSER [-v] [-nh]
```

### Options
* `-b BROWSER` or `--browser BROWSER`: Browser to use for survey automation. Currently, only `chrome` and `firefox` can be used.
* `-h` or `--help`: Show the help message.
* `-v` or `--verbose`: Print debugging messages during the merging process.
* `-nh` or `--noheadless`: Run the program with the browser window visible when automating surveys.

The program will first prompt you for which kind of survey you would like to automate. Depending on the survey selected, it will also prompt you for the appropriate information needed to start the survey.

If the information provided is incorrect or expired, the program will terminate the automation process automatically.

Once a survey has been successfully completed, the program will continue to prompt you for whether you would like to automate another survey.

## License
This project is licensed under the terms of the GNU GPL-3.0 license. See the `LICENSE` file for more information.
