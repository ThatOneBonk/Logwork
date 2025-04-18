from multiprocessing import Process, Queue
from collections import defaultdict
from argparse import Namespace
from typing import Optional
from enum import Enum
from os import path
import importlib
import argparse
import logging

from stream import stream_file

logging.basicConfig(encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportTypes(Enum):
    """
    The list of available report types. 
    Enum's `name` is the report type's name, Enum's `value` is the name of the module (file) used to create the corresponding report type.
    New report types must be added here. See README -> Adding reporters.
    """
    HANDLERS = "reporters.handlers"

def harvest_args() -> Namespace:
    """
    Provides hints for the `--help` argument and harvests any arguments passed.

    Args:
        None.

    Returns:
        Namespace: The parsed arguments as a Namespace object (`log_files` - log filenames (list), `report` - report type (str)).
    
    Raises:
        SystemExit: If required arguments aren't passed in the CLI or if --report type is not in ReportTypes.
    """
    parser = argparse.ArgumentParser(description="Logs analysis utility")

    parser.add_argument("log_files", nargs="+", help="paths to log files")

    parser.add_argument("--report", required=True,
    choices=[t.name.lower() for t in ReportTypes], # lower() for user-facing choice
    help="type of report to generate")

    args = parser.parse_args()
    args.report = args.report.upper() # upper() back again so it can be used later
    return args

def merge_dicts(individual_dict: dict, merged: defaultdict = None) -> defaultdict:
    """
    A helper function that takes a dictionary and merges it into a defaultdict. 
    The function's last output must be passed as the `merged` argument to merge multiple dictionaries.

    Args:
        individual_dict (dict): The dictionary that needs to be merged into the defaultdict.
            - Example format:
            {
                "/example1/": {"INFO": 20, "ERROR": 10}, 
                "/example2/": {"INFO": 15, "ERROR": 5}
            }
        merged (defaultdict): The result of previous merging. Defaults to None.

    Returns:
        defaultdict: The result of merging.
    """
    if not merged:
        merged = defaultdict(lambda: defaultdict(int))

    for url, log_dict in individual_dict.items():
        for log_level, count in log_dict.items():
            merged[url][log_level] += count

    return merged

def execute() -> Optional[str]:
    """
    This function ties other logic together.

    Args:
        None.

    Returns:
        Optional[str]: The program's output.
    """
    args = harvest_args()

    try:
        report_module = importlib.import_module(ReportTypes[args.report].value)
    except ImportError as e:
        logger.critical(f"%s: Failed to import module for {args.report}: {e}", execute.__name__)
        raise SystemExit(e) from e

    log_queue = Queue()
    worker_processes = []

    # dedicated loop to remove bad files because mutating the list you're working on (which, you could put this logic below, instead) can be dicey
    real_log_files = [file for file in args.log_files if path.exists(file)]
    for file in set(args.log_files) - set(real_log_files):
        logger.warning(f"%s: File `{file}` does not exist!", execute.__name__)

    for file in real_log_files:
        generator_function = stream_file(file)
        worker_process = Process(target=report_module.process_reports, args=(generator_function, log_queue))
        worker_processes.append(worker_process)
        logger.debug(f"%s: Starting reporter `{ReportTypes[args.report].name}` on file `{file}`", execute.__name__)
        worker_process.start()

    for worker_process in worker_processes:
        worker_process.join()

    merged = None

    if log_queue.empty():
        logger.warning("execute: Queue is empty. Nothing was generated.")
    else:
        while not log_queue.empty():
            merged = merge_dicts(log_queue.get(), merged)
        merged = {url: dict(logs) for url, logs in merged.items()}

    return report_module.assemble_output(merged)

if __name__ == "__main__":
    print(execute())
