import datetime


class DateTimeOps:
    """
    This class has methods for Date Time Operations.
    """
    
    def get_current_timestamp_utc(date_time_format: str) -> str:
        """
        Converts the date time by taking the required date time format and returns the UTC timestamp as a
        string in requested format.

        Args:
            date_time_format (str): a date time format as a string

        Returns:
            str: the UTC date time in specifiec format
        """        
        current_datetime = datetime.datetime.utcnow()
        timestamp = current_datetime.strftime(date_time_format)
        return timestamp
