Assignment
==========
Make python program that monitors web sites and reports their availability.

Requirements:
- Read URLs and corresponding page content requirements from a configuration file
- Periodically make HTTP request to each URL
- Verify page content
- Measure the time
- Write log file
- Content requirement can be simple string that must be included in the reponse
- Pay attention to design and be ready to defend architectural decisions

Background
==========
I got this assignment and it was supposed to do with Python. 
I have practically zero programming experience on Python. First I learned little bit 
about the language and the syntax at http://www.codecademy.com/en/tracks/python. 
Then I started experimenting with one requirement at a time. When I knew how to do 
things I designed the architecture and using the knowledge from the experiments 
I wrote the program. I made all this during Tuesday - Saturday. I spent about 2 days 
doing the course at codeacademy and 3 days experimenting with the code, 
designing architecture, writing program and reviewing the program and writing 
description. I used 5-8 hours per day for this project.

Running the program
===================
Program takes one argument from command line which is the period between URL polling in seconds. 

E.g. 10 second period: python checker.py 10

Program creates logging file of its behaviour on file my_program.log. The periodic check results are found in log_timestamp.txt.


Config file (config.txt)
===========
The file needs to be in the following format:
url expected_string
url expected_string
etc.

Meeting the requirements
========================

1. Reads a list of web pages (HTTP URLs) and corresponding page content requirements from a configuration file.

- The program reads URLs and expected page content from config.txt

2. Periodically makes an HTTP request to each page.

- The program takes command line argument which is used as a sleep time in the program before doing another check round of the URLs. 

3. Verifies that the page content received from the server matches the content requirements.

- The program compares document data got from the server and the expected content. 

4. Measures the time it took for the web server to complete the whole request.

5. Writes a log file that shows the progress of the periodic checks.

- The log file consists of Timestamp, HTTP Response code, Content requirement match result, Time the connection took and URL. 
- If there is error in connecting (e.g. malformed url) then message "Connection cannot be made (IOERROR) with the URL is written in the log. 

Describing the software
=======================

At first the program initializes logging. Then it reads the command line argument and saves the period time in variable. After that it reads config file and saves the URLs and expected content to dictionary. Then URLChecker object is created with the information previously read, plus with the log file name (log+timestamp.txt). Then we initialize the worker threads and after that launch the first check. 

The checking first populates the queue with URLs. Then the main thread waits until workers are done. When they are done it writes the generated log lines in the file, checks how long URL polling took and starts sleeping the time period given in the command line. If polling took more time than the given time period, then in the program log(my_program.log) is written WARNING and sleeping time is only 0.5 second. After sleep the rounds starts over by populating the queue and so on. 

Work threads get the URL from the queueu. Then they try to open the URL, read the result, close connection and check match between expected result and content read from the server. Then they prepare and write the log information to buffer that is later written on the log file. 