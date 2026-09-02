# Flask Backend App Template

## Overview
The **Flask Backend App Template** is an open-source project designed to streamline the development of RESTful APIs using Flask. It provides a robust and well-structured implementation with the following features:

- **SQLAlchemy**: Object-Relational Mapping (ORM) for database interactions.
- **JWT Authentication**: Predefined setup for secure authentication.
- **bcrypt**: Secure password hashing.
- **Flask-Migrate**: Simplifies database migrations.
- **Flask-CORS**: Handles Cross-Origin Resource Sharing.
- **PyMySQL**: MySQL database integration.

This template is ideal for developers looking to build scalable and secure APIs efficiently.

---

## Installation

### Step 1: Fork the Repository
1. Fork this repository on GitHub to your own account.

### Step 2: Create a New Repository from the Template
1. Click the **"Use this template"** button on the GitHub repository page.
2. Create a new repository from this template by providing a repository name and other details.

### Step 3: Clone the Repository
1. Clone your newly created repository to your local machine:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   ```
2. Navigate to the project directory:
   ```bash
   cd your-repo-name
   ```

### Step 4: Create a Virtual Environment (VENV)
```bash
python -m venv venv
```

### Step 5: Activate the Virtual Environment
#### For Git Bash or Unix-based Systems:
```bash
source venv/Scripts/activate
```
#### For Windows Command Prompt:
```cmd
venv\Scripts\activate
```

### Step 6: Install Required Packages
Install all necessary dependencies from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Step 7: Updating Requirements (Optional)
If you install any additional packages, update the `requirements.txt` file by running:
```bash
pip freeze > requirements.txt
```

---

## Database Connectivity

1. **Create a Database:**
   - Use tools like **XAMPP** or **WAMP** to create a new MySQL database.

2. **Create `.env` and Configure the Environment:**
   - Update the `.env` file with your database credentials, for example:
     
     ```env
     # Secrets
      JWT_SECRET_KEY = 'd8d13e7f3e5c6a02c46d3f2cb4f1b4c5'
      SECRET_KEY = 'bB@&2VbxD!yT5q!lKj*Wn?I}5M6xZ$@^'

      # Database URIs
      DATABASE_URI=mysql+pymysql://root:@localhost/db_name
     ```

---

## Flask Migration
Flask-Migrate helps manage database migrations. Follow these steps:

1. **Define Your Models:**
   - Add your models in the appropriate file (e.g., `models.py`) and reference them in `__init__.py`.

2. **Run Migration Commands:**
   - Initialize migrations:
     ```bash
     flask db init
     ```
   - Generate a new migration:
     ```bash
     flask db migrate -m "Migration message"
     ```
   - Apply migrations to the database:
     ```bash
     flask db upgrade
     ```

---

## Key Features

### 1. **Predefined Authentication Code**
Easily integrate secure JWT authentication into your API.

### 2. **Environment Management**
Use the `.env` file to manage configuration settings securely.

### 3. **Cross-Origin Requests**
Enable CORS to handle requests from different origins seamlessly.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to your branch (`git push origin feature-name`).
5. Create a pull request.

---

## Contact
If you have any questions or issues, feel free to open an issue on GitHub or contact the project maintainer.

