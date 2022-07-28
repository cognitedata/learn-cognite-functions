# Cognite Functions

[![Code Quality Checks](https://github.com/cognitedata/learn-cognite-functions/actions/workflows/code-quality.yaml/badge.svg)](https://github.com/cognitedata/learn-cognite-functions/actions/workflows/code-quality.yaml)


To get started with this repo :

1. First clone the repository, example such as
```
git clone git@github.com:cognitedata/learn-cognite-functions.git
```
2. Make sure that you've [poetry](https://python-poetry.org/) installed.
Also change the following setting in `poetry`
```
poetry config virtualenvs.in-project true
```
Open the repo in IDE (e.g. VS code) and run the following command in the terminal/commandline after navigating to the repo folder, this installs the dependencies defined in the `pyproject.toml` file.
```
poetry install
```
3. After that you're ready to run the code in notebooks folder.

Note : Additionally, Make sure you've created a ".env" file in the root folder of this repository, with the client secret value. ( A sample file named "save_this_as_dot_env" is available)

## Additional notes for developers:
4. Also install pre-commit hooks. ( Make sure you've [pre-commit](https://pre-commit.com/) installed prior to this command)
```
pre-commit install
```

Note : Before committing to github, Always run below command, to check that pre-commit checks are passed.
```
poetry run pre-commit run --all-files
``` 

5. Add new libraries as needed
```
poetry add pandas numpy
```
or if only required for development
```
poetry add --dev pandas
```