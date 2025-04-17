# Logwork
Does the legwork!
## What is this?
Logwork is a modular CLI application that processes log files using "reporter" modules. Reporter modules contain the report formation logic. The included reporter, `handlers`, considers `django.request` log entries from the Django framework logs, counts the number of messages by logging level and outputs the stats in a table. Example log files are included in this repository in the `example_logs` directory.
### Features
- Modular design;
- Extensive documentation;
- Multiprocessing capability.
## Adding reporters
Logwork was designed to be effortlessly extensible. Adding a reporter is as simple as putting it into the `reporters/` directory and including it in the ReportTypes Enum.
### Reporter specification
A reporter must have at least two modules - `process_reports` and `assemble_output`:
- `process_reports` must take the `generator` (`Generator[str, None, None]`) and the `queue` (`Queue`) arguments. 
    - `generator` links to the `stream_file` generator in `stream.py` which yields one log line at a time. 
    - `queue` is a processing queue where the function's output needs to be put.
    - A dictionary must be put into the queue. Example format:
    ```
        {
            "/example1/": {"INFO": 20, "ERROR": 10}, 
            "/example2/": {"INFO": 15, "ERROR": 5}
        }
    ```
- `assemble_output` must take the `data` (dict) argument (example format above) and return a string. The string will be printed into the console as the program's output.
### Adding a reporter
Reporters must be put in the `reporters/` directory with an arbitrary name.
Reporters must be included in the ReporterTypes Enum in `main.py`. 
- The Enum's name is the reporter's alias, the name of the argument that will need to be passed as the --report argument to invoke it. 
- The Enum's value is the path to the reporter. Assuming it's in the `reporters/` directory, it will be something like `reporters.<name>` (without the .py postfx).
## Usage
- `git clone https://github.com/ThatOneBonk/Logwork.git`
- `python main.py <log paths> --report <reporter alias>`
### Example screenshot
![Example screenshot](assets/example_screenshot.png)