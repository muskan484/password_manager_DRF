The Password Manager project is a RESTful API built using Django Rest Framework. It utilizes SQLite as the primary database for storing data. The project employs Celery in conjunction with Redis as a message broker to handle tasks such as sending emails to users and performing weekly backups of data to Firebase Cloud Storage. Authentication in the project is implemented using JSON Web Tokens (JWT), providing secure access to users' accounts and resources.

## Installation

1. Clone the repository:

git clone "URL",

2. Commands to run the project
    - python3 -m venv <ENV_NAME>
    - source <ENV_NAME>/bin/activate
    - pip3 install -r requirements.txt
    - Migrations for database 
        python3 manage.py makemigrations
        python3 manage.py migrate
    - Create Superuser
        python3 manage.py createsuperuser    
    - Start the development server:
        python3 manage.py runserver
    - Run redis-server
        redis-server
    - Run celery worker
        celery -A password_manager worker --loglevel=info
    - Run celery beat
        celery -A password_manager beat --loglevel=info

## Models

### User Model
- username: Unique identifier for the user.
- first_name: User's first name
- last_name: User's last name
- email: User's email address, also unique.
- password: User's password for authentication.

## Password Vault Model
- user: username of current active user.
- website_name: Indicates the name of the website associated with the password.
- website_url: website URL associated with the password.
- password: It stores the password associated with the website.
- created_at: Automatically capturing the date and time when the password record is created.

## Usage 

### User Profile Management

#### User Registration

- POST api/user/register

Example request body:
```
{
    "username":"John01",
    "first_name":"John",
    "last_name":"Brown",
    "email":"john.brown@gmail.com",
    "password":"JohnB#0392",
    "confirm_password":"JohnB#0392"
}
```

#### User Login

- POST api/user/login

Example request body:
```
{
    "username":"John01",
    "password":"JohnB#0392"
}
```

### Password Management

#### Add Password

- POST api/password/add

Example request body:
```
{
    "website_name": "google",
    "website_url": "https://www.google.com",
    "password": "Google#@9810"
}
```

- POST api/password/add?autogenerate=True

Example request body:
```
{
    "website_name": "google",
    "website_url": "https://www.google.com"
}
```

#### Update Password

- POST api/password/update

Example request body:
```
{
    "website_name": "google",
    "website_url": "https://www.google.com",
    "old_password": "Google#@9810",
    "new_password": "Google_new#@9810",
}
```

#### Delete Password

- GET api/password/delete?website_name='google'

Example response body:
```
{
    "Message":f"Password for {website_name} deleted successfully"
}
```

#### View ALl Password

- GET api/password/all

Example response body:
```
[
    {
    "id": 2,
    "user": "John01",
    "website_name": "google",
    "website_url": "https://www.google.com",
    "password": "fX3|bO2.vE8^",
    "created_at": "2024-01-02T21:10:57.879697Z"
    }
    ...
]
```

## Email Notifications

- User Registration: Upon successful registration, a welcome email is sent to the user's email address.
- Adding a New Password: When a user adds a new password to their vault, a confirmation email is sent to notify the user about the addition.
- Password Update: After a user updates a password, a notification email is sent to confirm the successful update.
- Weekly Database Backup: Every week, a scheduled task is executed using Celery to back up the database. The data is then securely stored in Firebase Cloud Storage for additional security and data integrity.

## Authentication

- Authentication in the project is implemented using JSON Web Tokens (JWT). JWT provides secure access to users' accounts and resources by generating a token upon successful authentication. This token is then used to authorize and authenticate subsequent requests made by the user.

By leveraging Celery, Redis, and JWT, the Password Manager project ensures efficient task handling, secure user authentication, and reliable email notifications for enhanced user experience and data security.