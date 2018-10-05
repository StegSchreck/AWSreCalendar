# AWSreCalendar

This project takes the data for your favourited sessions of the AWS re:Invent and prints them grouped by date and sorted by time.
It has no ability yet to mark potential conflicts, but can be a help when trying to see if the sessions you are interested in are feasible to combine.

**NOTE**: This project is not affiliated in any way with Amazon Web Services.


## Preconditions
1. Make sure you have Python3, Firefox and Xvfb installed on your system. This project is designed to run on Linux.
1. Checkout the project
    `git clone https://github.com/StegSchreck/AWSreCalendar.git && cd AWSreCalendar`
1. Install the requirements with pip for Python3
    `pip3 install -r requirements.txt`
1. Install Geckodriver

      * Use your system's package manager (if it contains Geckodriver)
        * Arch Linux: `pacman -S geckodriver`
        * MacOS: `brew install geckodriver`
      * Or execute `sudo ./InstallGeckodriver.sh`.
        For this you will need to have tar and wget installed.


## Running the script
The basic command looks as follows:
```
python3 main.py -u <your.name@domain.com> -p <your_secret_password>
```
You can filter the output by using the parameters described below.


## Call arguments / parameters
### Mandatory
`-u` / `--username`: username for AWS re:Invent login

`-p` / `--password`: password for AWS re:Invent login

### Optional
`-d` / `--day`: Filter output to only include this day. Possible values include e.g. '2018-11-26', 'Tuesday', 'fr'. This is not case sensitive.

`-s` / `--speaker`: Filter output to only include items with given speaker name, e.g. 'Werner', 'Vogels'. This is not case sensitive.

`-t` / `--type`: Filter output to only include this type of sessions. Possible values include e.g. 'Session', 'Workshop'. This is not case sensitive.

`-l` / `--location`: Filter output to only include locations containing given text. Possible values include e.g. 'Venetian', 'Grand Ballroom B'. This is not case sensitive.

`-n` / `--name`: Filter output to only include items with given text in the title. This is not case sensitive.

`-a` / `--abstract`: Filter output to only include items with given text in the abstract. This is not case sensitive.

`-A` / `--show_abstract`: show the session description in output

`-f` / `--file`: Load data from this file instead of parsing the page again. The file has to be next to be in the same folder.

`-v` / `--verbose`: increase output verbosity

`-x` / `--show_browser`: show the browser doing his work (this might help for debugging)

`-h` / `--help`: Display the help, including all possible parameter options


## Trouble shooting
### Script aborts with `WebDriverException`
If you recently updated your Firefox, you might encounter the following exception during the login attempt of the parser:
```
selenium.common.exceptions.WebDriverException: Message: Expected [object Undefined] undefined to be a string
```

This can be fixed by installing the latest version of [Mozilla's Geckodriver](https://github.com/mozilla/geckodriver)
by running again the _Install Geckodriver_ command mentioned [above](#preconditions).

### Login attempt does not work
This can have multiple explanations. One is, that you are using a password which starts or ends with a space character.
This script is currently not capable of dealing with that.
If your credentials have a space character in the middle though, it will work fine. 