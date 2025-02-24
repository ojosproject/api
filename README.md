# ojos-flask-twilio

This is a Python project that uses Flask to allow Iris to send sms messages and
emails to patients and caretakers with API calls to Twilio

## Installation

Use [pip](https://pip.pypa.io/en/stable/) to install dependencies

```bash
python -m venv venv
venv\Scripts\activate # check https://docs.python.org/3/library/venv.html#how-venvs-work
pip install -r requirements.txt
```

```bash
flask --app src.app run
```

To run tests, run:

```shell
coverage run -m pytest
coverage xml
```

If you're using Visual Studio Code, install the
[Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters)
extension to see the code coverage.

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
