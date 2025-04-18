from multiprocessing import Queue
from textwrap import dedent

import pytest

from reporters.handlers import assemble_output, process_reports

@pytest.fixture
def log_dict():
    """
    A pytest fixture containing the default input dict for assemble_output().
    """
    return  {
        '/api/v1/reviews/': {'INFO': 20, 'ERROR': 4}, 
        '/admin/dashboard/': {'INFO': 13, 'ERROR': 4}, 
        '/api/v1/users/': {'INFO': 9, 'ERROR': 3}, 
        '/api/v1/cart/': {'INFO': 9, 'ERROR': 1},
    }

def test_process_reports_basic_case():
    """
    Should parse the fake yield contents properly.
    """
    def fake_generator():
        yield "2025-04-17 12:00:00,000 INFO django.request: Something happened /api/v1/cart/ more info"
        yield "2025-04-17 12:00:01,000 ERROR django.request: Something failed /api/v1/cart/ failed hard :("
        yield "2025-04-17 12:00:02,000 WARNING django.security: Ignore me /api/v1/users/"
        yield "2025-04-17 12:00:03,000 INFO django.request: Request OK /api/v1/users/ all good :)"

    queue = Queue()

    process_reports(fake_generator(), queue)

    result = queue.get()
    expected = {
        '/api/v1/cart/': {'INFO': 1, 'ERROR': 1},
        '/api/v1/users/': {'INFO': 1}
    }

    assert result == expected

def test_assemble_output_valid_input(log_dict):
    """
    Should return a properly formatted string.
    """
    result = assemble_output(log_dict)
    expected = dedent("""\
        Total requests: 63

        HANDLER                  DEBUG     INFO      WARNING   ERROR     CRITICAL  
        /admin/dashboard/        0         13        0         4         0         
        /api/v1/cart/            0         9         0         1         0         
        /api/v1/reviews/         0         20        0         4         0         
        /api/v1/users/           0         9         0         3         0         
                                 0         51        0         12        0         """)
    assert result == expected