from collections import defaultdict
from argparse import Namespace
import sys

from unittest.mock import patch, MagicMock
import pytest

from main import harvest_args, merge_dicts, execute
import main

@pytest.fixture
def log_dicts():
    """
    A pytest fixture containing the default input dicts for merge_dicts().
    """
    return {
        "first": {
            "/example1/": {"INFO": 20, "ERROR": 10},
            "/example2/": {"INFO": 15, "ERROR": 5}
        },
        "second": {
            "/example1/": {"INFO": 15, "ERROR": 1},
            "/example2/": {"INFO": 5}
        }
    }

def test_harvest_args_valid_input(monkeypatch):
    """
    Should return a list of log file paths and the handler name in uppercase.
    """
    test_args = ["main.py", "log1.txt", "log2.txt", "--report", "handlers"]
    monkeypatch.setattr(sys, "argv", test_args)

    args = harvest_args()
    assert isinstance(args, Namespace)
    assert args.log_files == ["log1.txt", "log2.txt"]
    assert args.report == "HANDLERS"

def test_harvest_args_raises_if_report_missing(monkeypatch):
    """
    Should raise SystemExit if the --report argument is not passed.
    """
    test_args = ["main.py", "log1.txt", "log2.txt"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit):
        harvest_args()

def test_harvest_args_raises_if_report_bad(monkeypatch):
    """
    Should raise SystemExit if a non-existent --report type is passed.
    """
    test_args = ["main.py", "log1.txt", "log2.txt", "--report", "ThisReportTypeDoesNotExist"]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit):
        harvest_args()


def test_merge_dicts_single_input(log_dicts):
    """
    Should properly merge a single dict into the output.
    """
    function_output = merge_dicts(log_dicts["first"])

    assert function_output.default_factory is not None
    assert isinstance(function_output, defaultdict)
    assert isinstance(function_output["/example1/"], defaultdict)

    assert function_output["/example1/"]["INFO"] == 20
    assert function_output["/example1/"]["ERROR"] == 10
    assert function_output["/example2/"]["INFO"] == 15
    assert function_output["/example2/"]["ERROR"] == 5
    assert function_output["/example2/"]["CRITICAL"] == 0

def test_merge_dicts_multi_input(log_dicts):
    """
    Should properly merge two dicts into a single output.
    """

    function_first_output = merge_dicts(log_dicts["first"])
    function_final_output = merge_dicts(log_dicts["second"], function_first_output)

    assert function_final_output.default_factory is not None
    assert isinstance(function_final_output, defaultdict)
    assert isinstance(function_final_output["/example1/"], defaultdict)

    assert function_final_output["/example1/"]["INFO"] == 35
    assert function_final_output["/example1/"]["ERROR"] == 11
    assert function_final_output["/example2/"]["INFO"] == 20
    assert function_final_output["/example2/"]["ERROR"] == 5
    assert function_final_output["/example2/"]["CRITICAL"] == 0


@patch('main.importlib.import_module')
def test_execute_bad_module(mock_import_module):
    """
    Should raise SystemExit.
    """

    with patch.object(main, "harvest_args", return_value=Namespace(log_files=['app1.log', 'app2.log'], report='HANDLERS')):
        mock_import_module.side_effect = ImportError
        with pytest.raises(SystemExit):
            execute()

def test_execute_valid_input(log_dicts):
    """
    Should call the mock reporter assembler function and output its return without errors.
    """
    mock_reporter = MagicMock()
    mock_reporter.process_reports.return_value = log_dicts["first"]
    mock_reporter.assemble_output.return_value = "pretend this is proper output"

    with patch.object(main, "harvest_args", return_value=Namespace(log_files=['app1.log', 'app2.log'], report='HANDLERS')),\
    patch("importlib.import_module", return_value=mock_reporter):
        function_output = execute()
        assert function_output == "pretend this is proper output"