# CALPULLI

CALPULLI is a platform that enables users to train machine learning models while preserving the privacy of their data. It provides a secure environment for training and inference, allowing users to leverage the power of machine learning without compromising their data privacy.

## Requirements
- Python 3.10 or higher (recommended to use [pyenv](https://github.com/pyenv/pyenv) for managing Python versions)
- Poetry for dependency management `pip3 install poetry` 
- Poetry shell for activating the virtual environment `poetry self add poetry-plugin-shell`
- Git for version control
- Docker for containerization (optional, but recommended for development and deployment)

## Getting started
To get started with CALPULLI, follow these steps:
1. Clone the repository: `git clone git@github.com:Ismael-droid-01/calpulli-api.git`
2. Navigate to the project directory: `cd calpulli-api`
3. Activate the virtual environment: `poetry shell`
4. Install the dependencies: `poetry install`
5. Deploy the platform using Docker: `docker-compose --env-file .env.dev -f docker-compose.yml up --build` or run the bash script `deploy.sh` for a more streamlined deployment process.
6. Access the platform at [http://localhost:6000/docs](http://localhost:6000/docs)

### Local Development
For local development, you can run the FastAPI server directly without Docker:
1. Activate the virtual environment: `poetry shell`
2. Deploy the database and Xolo services using Docker Compose and select only the development profile: `docker-compose --profile dev --env-file .env.dev -f docker-compose.yml up`
2. Start the FastAPI server: `uvicorn ppml.server:app --host ${CALPULLI_HOST:-0.0.0.0} --port ${CALPULLI_PORT:-5000} --reload`
This will start the server with hot-reloading enabled, allowing you to see changes in real-time.

## Contributing
Contributions to CALPULLI are welcome! If you have an idea for a new feature or improvement, please open an issue or submit a pull request. Please make sure to follow the code of conduct and the contribution guidelines.

## License
CALPULLI is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
