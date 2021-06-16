"""
log_to_file.py

Contains methods for outputting log data into a text file.

Anatoly Zavyalov, 2021
"""

from datetime import datetime

def log_to_file(message: str, urgency: int=0, file_location: str='log.txt') -> None:
    """Append a log message to :param file_location: with the format `[TIME] | :param urgency: | :param message:`. Time will be added automatically.

    :param message: The message to log
    :type message: str
    :param urgency: The urgency level of the log message. 0 is "INFO", 1 is "WARN", 2 is "ERROR", "UNDEF" otherwise.
    :type urgency: int
    :param file_location: The location of the log file to output to, defaults to 'log.txt'
    :type file_location: str, optional
    """

    # Using 'with' will automatically close the log file.
    with open(file_location, 'a') as file:

        if urgency == 0:
            urgency_msg = "INFO"

        elif urgency == 1:
            urgency_msg = "WARN"

        elif urgency == 2:
            urgency_msg = "ERROR"

        else:
            urgency_msg = "UNDEF"

            log_to_file(message=f"Urgency value out of bounds: {urgency}, expected: 0, 1, 2.", urgency=1)

        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \t | \t {urgency_msg} \t | \t {message}\n')
