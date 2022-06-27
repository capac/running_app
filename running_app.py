from running_app.application import Application
import logging

# initialize the log settings
# https://code.tutsplus.com/tutorials/error-handling-logging-in-python--cms-27932
logging.basicConfig(filename='app.log', level=logging.INFO)

try:
    app = Application()
    app.mainloop()
except IOError as e:
    logging.exception(str(e))
