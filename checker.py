"""
Created on Nov 20, 2014

@author: Vili
"""
import urllib
import time
from datetime import datetime
import argparse
import logging
from threading import Thread
from Queue import Queue


class URLChecker(object):
    """ Tries to contact given URL-list one at a time. If url is connected then
    checks if the returned document has expected string in it. Finally writes
    results in the given log file. This runs indefinitely in a thread.
    """

    thread_number = 10
    q = Queue(maxsize=0)
    to_log_file = ""

    def __init__(self, url_dictionary, seconds_to_sleep, log_file_name):
        """ Initialize by giving urls and expected content in dictionary,
        period to the check in seconds (sleep time) and log file name.
        """
        logging.info("Initializing URLChecker")
        self.url_dictionary = url_dictionary
        self.seconds_to_sleep = seconds_to_sleep
        self.log_file_name = log_file_name

    def check_url(self, url):
        """ Connects to the given url, reads the document and makes the content
        requirement check. Returns the result in a ready log line. Remember
        that url parameter is also key in the url_dictionary that has expected
        value.
        """
        expected_result = self.url_dictionary[url]
        try:
            logging.debug("Start network connection")
            start_time = time.clock()
            conn = urllib.urlopen(url)
            status = str(conn.getcode())
            result = conn.read()
            conn.close()
            end_time = time.clock()
            logging.debug("End network connection")
        except IOError:
            logging.info("IOERROR in networking")
            log_line = self.get_timestamp() + " Connection cannot be made\
            (IOERROR), URL: " + url
        else:
            content_requirement_match = self.check_content_requirement(expected_result, result)
            # Return what to write in LOG file
            log_line = self.get_timestamp() + " Response code: " + status + ",\
             Content requirement match: " + str(content_requirement_match) + ",\
              Time: " + str(end_time - start_time) + " seconds, URL: " + url
        return log_line

    def check_content_requirement(self, expected, content):
        """ Check if expected value is in the content from server."""
        if expected in content:
            return True
        else:
            return False

    def write_log_line(self, content_to_file):
        with open(self.log_file_name, "a") as log_file:
            log_file.write(content_to_file)

    def get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def populate_urls(self):
        """ Give workers urls to check."""
        logging.debug("Populating urls")
        for url in self.url_dictionary:
            self.q.put(url)

    def init_workers(self):
        """Start working threads."""
        logging.info("Starting workers")
        for i in range(self.thread_number):
            worker = Thread(target=self.do_work, args=(self.q,))
            worker.start()
        logging.debug("Workers started, waiting...")

    def start_running(self):
        """Gives workers something to do, waits until all are finished. 
        Then writes results to file, sleeps given period and starts
        all over again.
        """
        start_time = time.clock()
        self.populate_urls()
        while True:
            self.q.join()
            logging.info("Wait over, writing to log file")
            logging.debug("String to file: " + self.to_log_file)
            self.write_log(self.to_log_file)
            self.to_log_file = ""
            end_time = time.clock()
            sleep_time = self.seconds_to_sleep - (end_time - start_time)
            if sleep_time < 0:
                logging.warn("Sleep time longer than period.")
                sleep_time = 0.5
            logging.info("Sleeping " + str(sleep_time) + " seconds")
            time.sleep(float(sleep_time))
            start_time = time.clock()
            self.populate_urls()

    def do_work(self, q):
        """Workers work method. Get url, make check for that url,
        append information to log buffer and report work is done.
        """
        while True:
            my_url = q.get()
            log_line = self.check_url(my_url)
            self.append_to_log_buffer(log_line)
            q.task_done()

    def append_to_log_buffer(self, one_log_line):
        self.to_log_file += one_log_line + "\n"

    def write_log(self, content_to_file):
        with open(self.log_file_name, "a") as log_file:
            log_file.write(content_to_file)


def read_args():
    """ Read command line arguments. """
    logging.info("Reading config info")
    parser = argparse.ArgumentParser()
    parser.add_argument("sleep", help="Time period in secondsthe program \
    waits between polling urls.", type=int)
    args = parser.parse_args()
    return args.sleep


def read_config_file(name):
    """ Read given config file into dictionary and return it."""
    data = {}
    with open(name, "r") as conf:
        for line in conf:
            item = line.split()
            key = item[0]
            value = item[1]
            data[key] = value
    return data


def define_logging():
    """Set up the logging."""
    logging.basicConfig(filename="my_program.log", level=logging.DEBUG)


def main():
    """ Main function to start url polling."""
    define_logging()
    logging.info("Program started")
    seconds_to_sleep = read_args()
    # seconds_to_sleep = 5
    config_dict = read_config_file("config.txt")
    checker = URLChecker(config_dict, seconds_to_sleep, "log_" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".txt")
    checker.init_workers()
    checker.start_running()

# Call main function
if __name__ == '__main__':
    main()
