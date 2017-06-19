import sys
import os
import datetime




LOG_DIR = "logs"
__LOG_FILE = LOG_DIR+"/"+"program.log"




__HAS_RUN = False
def __log(msg):
	global __HAS_RUN
	if not os.path.isdir(LOG_DIR):
		os.makedirs(LOG_DIR)
	if not __HAS_RUN and os.path.isfile(__LOG_FILE):
		os.remove(__LOG_FILE)
		__HAS_RUN = True
	print msg
	with open(__LOG_FILE,'a') as f:
		f.write("{}\n".format(msg))

def log(msg):
	__log(msg)



errors = []

def log_error(err_msg, shutdown=False):
	__log("ERROR ------------------------------------------------------")
	__log(err_msg)
	__log("------------------------------------------------------------")
	if shutdown:
		raise RuntimeError("Error occurred. See log error above.")
	else:
		errors.append(err_msg)



def get_errors_str():
	errors_str = "\n";
	for err in errors:
		errors_str += err + "\n"
	return errors_str



def log_segment(segment_title):
	'''
	__log("")
	__log(":::::::::::::::::::::::::::::::::::::::::::  {}".format(segment_title))
	'''
	timestamp = "{}  ".format(datetime.datetime.now())
	segment_title = "  " + segment_title
	l = len(timestamp)
	total_len = 60
	formatted_msg =  timestamp + (':' * (total_len - l)) + segment_title
	__log(formatted_msg)



def log_start(start_msg):
	__log("")
	__log("")
	__log("============================================================")
	__log(start_msg)
	__log("============================================================")



def log_stop(stop_msg):
	__log("")
	__log("============================================================")
	__log(stop_msg)
	__log("============================================================")
	__log("")
