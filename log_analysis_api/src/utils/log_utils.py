import logging as lg
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import time
from typing import Any
    
class LoggingUtils:
    """
    Contains methods for Log operations
    """
    def time_rotated_log(props: Any, log_dir_path: str) -> lg.Logger:
        """
        Takes properties and log directory path and returns an object for time rotated logging
        with specified format.

        Args:
            props (Any): Object with properties from yaml config
            log_dir_path (str): path of the application logs directory

        Returns:
            lg.Logger: Formatted instance of Logging Object
        """
        log_data_file = log_dir_path+"_".join([datetime.utcnow().strftime(props.applog_prefix), props.applog_suffix])
        lg.getLogger()
        lg.Formatter.converter = time.gmtime
        time_handler=TimedRotatingFileHandler(log_data_file,utc=True,when='midnight',encoding='utf-8')
        stream_handler=lg.StreamHandler()
        
        lg.basicConfig(format=props.applog_message_format,
                       level=lg.INFO,
                       handlers=[time_handler, stream_handler])
        
        return lg