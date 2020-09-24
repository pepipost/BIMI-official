import logging as logger
from Config import Config
from datetime import date
from utils.Utils import Utils
log_level = Config.LOGGING_LEVEL
log_file_path = Config.LOG_FILE_PATH+str(date.today()) +"_"+Config.LOG_FILE_NAME
Utils = Utils()
Utils.check_dir_folder(Config.LOG_FILE_PATH)

if log_level=="INFO":
	log_level=logger.INFO
elif log_level=="DEBUG":
	log_level=logger.DEBUG
elif log_level=="WARNING":
	log_level=logger.WARN
else:
	log_level=logger.INFO

logger.basicConfig(
		filename = log_file_path,
		filemode='a',
		format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
		datefmt='%m/%d/%Y %H:%M:%S',
		level=log_level
	)