# PRIVACY PRESERVING ML PLATFORM (PPMLP)

PPMLP is a platform that enables users to train machine learning models while preserving the privacy of their data. It provides a secure environment for training and inference, allowing users to leverage the power of machine learning without compromising their data privacy.

## Requirements
- Python 3.10 or higher (recommended to use [pyenv](https://github.com/pyenv/pyenv) for managing Python versions)
- Poetry for dependency management `pip3 install poetry` 
- Poetry shell for activating the virtual environment `poetry self add poetry-plugin-shell`
- Git for version control
- Docker for containerization (optional, but recommended for development and deployment)

## Getting started
To get started with PPMLP, follow these steps:
1. Clone the repository: `git clone git@github.com:Ismael-droid-01/privacy-preserving-ml-platform.git`
2. Navigate to the project directory: `cd privacy-preserving-ml-platform`
3. Activate the virtual environment: `poetry shell`
4. Install the dependencies: `poetry install`
5. Deploy the platform using Docker: `docker-compose --env-file .env.dev -f docker-compose.yml up --build` or run the bash script `deploy.sh` for a more streamlined deployment process.
6. Access the platform at [http://localhost:6000/docs](http://localhost:6000/docs)

