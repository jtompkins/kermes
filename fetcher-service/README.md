## Local Development

1. Switch to the virtualenv: `poetry shell`
1. In VS Code, ensure that you're using the virtual env python (look for the application name in the list of python interpreters)
1. Start a localstack instance in Docker in a different terminal (but in the venv shell): `localstack start`
1. Localstack runs all of the supported AWS services locally; to point the AWS CLI at it, add this to the command: `--endpoint-url=http://localhost:4566` before the AWS subcommand
