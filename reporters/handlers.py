from collections import defaultdict
from multiprocessing import Queue
from typing import Generator
import logging
import re

logger = logging.getLogger(__name__)

def process_reports(generator: Generator[str, None, None], queue: Queue):
    """
    Processes yielded log lines into a `defaultdict` and puts the result into a processing `Queue`.

    Args:
        generator (Generator[str]): A generator function that will yield one line of a text (log) file at a time.
        queue (Queue): The processing queue in which to put the result.

    Returns:
        None.
    """
    output = defaultdict(lambda: defaultdict(int))
    pattern = re.compile(r'(?P<level>[A-Z]+)\s(?P<module>[\w\.]+):.*?\s(?P<path>/[^\s]+)\s')
    for line in generator:
        # skips lines without wanted module as an optimization (it's still regexed later just in case)
        if "django.request" in line:
            matches = re.search(pattern, line[24:])

            if matches:
                log_level = matches.group("level")
                log_module = matches.group("module")
                log_handler_path = matches.group("path")

                # still check for this, because django.request could appear somewhere else in the log and trip up the above check, we'll never know
                if log_module == "django.request":
                    output[log_handler_path][log_level] += 1

    queue.put({path: dict(levels) for path, levels in output.items()})

def assemble_output(data: dict) -> str:
    """
    Formats `data` into a human-readable table for output.

    Args:
        data (dict): The dataset that needs to be formatted.
            Example:
            {
                "/example1/": {"INFO": 20, "ERROR": 10}, 
                "/example2/": {"INFO": 15, "ERROR": 5}
            }
        
    Returns:
        str: A user-friendly table. Example output:

            Total requests: 50

            HANDLER     DEBUG   INFO    WARNING     ERROR   CRITICAL
            /example1/  0       20      0           10      0
            /example2/  0       15      0           5       0
                        0       35      0           15      0

    """
    sorted_log_data = dict(sorted(data.items()))
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    output = ""
    total_counts = defaultdict(int)

    header = f"{'HANDLER':<25}" + "".join(f"{lvl:<10}" for lvl in log_levels)
    output += header + "\n"

    for handler, counts in sorted_log_data.items():
        row = [handler.ljust(25)]
        for level in log_levels:
            value = counts.get(level, 0)
            total_counts[level] += value
            row.append(str(value).ljust(10))
        output += "".join(row) + "\n"

    total_row = ["".ljust(25)] + [str(total_counts[level]).ljust(10) for level in log_levels]
    output += "".join(total_row)

    total_requests = sum(total_counts.values())
    output = f"Total requests: {total_requests}\n\n" + output

    return output
