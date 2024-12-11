# FastAPI Starter Package

This is a simple starter template designed to help you quickly set up a project with **FastAPI**.

## Project Structure

The package comes with a structured directory layout to ensure maintainability and scalability. Here's a breakdown of each directory and file:

### Directories

- **`api/`**: This directory is used to handle all your API endpoints, with version control implemented to organize them effectively.
  
- **`middlewares/`**: Place all your custom middleware files here. Each middleware can be managed in individual files for clarity.
  
- **`models/`**: All database models should be placed here. You can have multiple files based on the different types of models you are working with.

- **`serializers/`**: This folder contains your Pydantic models (serializers) for validating and serializing data. You can split them into multiple files as needed.

- **`services/`**: This directory should contain all your business logic and service functions.

- **`tests/`**: If you have written any test cases, this is where they should go. All your test-related files can be organized in this directory.

### Files

- **`config.py`**: This file holds the settings class, where you should store all your constants and secret keys. The values defined here can be accessed throughout the entire project.

- **`dependencies.py`**: This file contains any dependencies you define, which can be used across different parts of the application.

- **`main.py`**: This is the entry point of the FastAPI application. It initializes the FastAPI instance, configures middlewares, and defines application events.

- **`utils.py`**: This file contains any helper functions that will be reused throughout the project. Common utilities can be centralized here for easy access.

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd <project_folder>
   ```

2. **Install dependencies**:
    ```bash
    pip install "fastapi[standard]"
    pip install "fastapi-jwt[authlib]"
    pip install mailjet_rest
    pip install alembic
    pip install passlib
    ```

3. **Run the application**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Customization
You can customize the project structure by adding or modifying the folders and files to suit your needs. The basic structure ensures that your code remains modular and easy to maintain.

## License
This project is licensed under the MIT License...

<br/>

# Muhammad Bilal Azaad