- Installation and requirements:
    - Install fast API and Uvicorn(ASGI server)
    ```pip install fastapi```
    ```pip install uvicorn``` 

    - Other Requirements
    ```pip install asyncpg psycopg2 psycopg2 psycopg2-binary alembic python-decouple sqlalchemy databases bcrypt```

    - Azyncclick - used to manage super users without needing to write directly in database
    ```pip install asyncclick```

    - Launch app
    ```uvicorn main:app --reload```

    - Authentication
    ```pip install pyjwt```

- Create models:
    - Set up
        - Create package directory
        Create a directory called ```models``` and within it we will create a ```__init__.py``` file. We'll get back to it
        though this one should contain the model imports, for exambple:
        ```python
        from models.complaint import *
        from models.user import *
        ```

        - Files or models
        We will proceed to create our a file per model we're using. Using the previous example we can create a ```complaint.py``` and ```user.py``` model. We can create an ```enums.py``` file as well, though make sure it is in plural to avoid confusion during execution with package named ```enum```,

        - Sample Model
        ```python
        import sqlalchemy

        from db import metadata
        from models.enums import State

        complaint = sqlalchemy.Table(
            "complaints",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("title", sqlalchemy.String(120), nullable=False),
            sqlalchemy.Column("description", sqlalchemy.Text, nullable=False),
            sqlalchemy.Column("photo_url", sqlalchemy.String(200), nullable=False),
            sqlalchemy.Column("amount", sqlalchemy.Float, nullable=False),
            sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
            sqlalchemy.Column("status", sqlalchemy.Enum(State), nullable=False, server_default=State.pending.name),
            sqlalchemy.Column("complainer_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
        )
        ```

        - Sample Enum
        ```python
        import enum


        class RoleType(enum.Enum):
            approver = "approver"
            complainer = "complainer"
            admin = "admin"


        class State(enum.Enum):
            pending = "Pending"
            approved = "Approved"
            rejected = "Rejected"
        ```

- Migrations
    - Create Migrations
    We need to create our migrations with the following command ```alembic init migrations```. This will generate a ```migrations``` folder.

    - Modify .env, migration -> env.py and alembic.ini

        - Migrations - env.py file sample
        In the migrations directory modify the ```env.py``` file
        ```python
        from logging.config import fileConfig

        from sqlalchemy import engine_from_config
        from sqlalchemy import pool

        from alembic import context
        ## >>>>> ADDED IMPORTS --------------------
        from decouple import config as env_config
        from db import metadata
        import models
        ## -----------------------------------<<<<<

        # this is the Alembic Config object, which provides
        # access to the values within the .ini file in use.
        config = context.config

        ## >>>>> SETTING UP CREDENTIALS -----------
        section = config.config_ini_section
        config.set_section_option(section, "DB_USER", env_config("DB_USER"))
        config.set_section_option(section, "DB_PASS", env_config("DB_PASS"))
        config.set_section_option(section, "DB_SERVER", env_config("DB_SERVER"))
        config.set_section_option(section, "DB_NAME", env_config("DB_NAME"))
        config.set_section_option(section, "DB_PORT", env_config("DB_PORT"))
        ## -----------------------------------<<<<<

        # Interpret the config file for Python logging.
        # This line sets up loggers basically.
        if config.config_file_name is not None:
            fileConfig(config.config_file_name)

        # add your model's MetaData object here
        # for 'autogenerate' support
        # from myapp import mymodel
        # target_metadata = mymodel.Base.metadata
        ## >>>>> USING METADATA -------------------
        target_metadata = metadata
        ## -----------------------------------<<<<<
        ```
        
        - .env sample file
        Create a ```.env``` file in the main directory to place sensitive information.
        NOTE - Remember to ignore this on your ```gitignore``` instruction to avoid uploading and exposing your keys.
        ```python
        DB_USER=username
        DB_PASS=password123
        DB_PORT=5432
        DB_NAME=complaints
        DB_SERVER =localhost
        JWT_SECRET = jwtsecret123
        ```

        - alembic.ini changes
        Modify the ```alembic.ini file``` to match your database connection url.
        ```
        sqlalchemy.url = postgresql://%(DB_USER)s:%(DB_PASS)s@%(DB_SERVER)s:%(DB_PORT)s/%(DB_NAME)s
        ```
    
    - Create Migration
    We're going to create the migration by executing the following command: ```alembic revision --autogenerate -m "Notes to add"```
    
    An error can occur if database doesn't exists. Or exists with data.
    Also make sure Database credentials and information matches the real information.
    
    - Upgrade Migration
    To point to the the most recent migration execute the following command: ```alembic upgrade head```

- Resources
The intenmmtion of this package is to store our application endpoints.
Create package ```resources``` by creating a directory on root folder and within it create a file called ```__init__.py```. 
   
   - auth
    ```python
    from fastapi import APIRouter
    from managers.user import UserManager

    router = APIRouter(tags=["Auth"])


    @router.post("/register/", status_code=201)
    async def register(user_data):
        token = await UserManager.register(user_data)
        return {"token": token}
    ```

  - routes
  Imports ```router``` declared on the ```auth.py``` file>
    ```python
    from fastapi import APIRouter
    from resources import auth

    api_router = APIRouter()
    api_router.include_router(auth.router)
    ```

  Then this will need to referenced in the ```main.py``` file.
    ```python
    from resources.routes import api_router

    app = FastAPI()
    app.include_router(api_router)
    ```

- Managers
It is recommended to create a ```managers``` package, where things like authentication can be defined.
Create package ```managers``` by creating a directory on root folder and within it create a file called ```__init__.py```.

  - Authentication
    Within this package create an ```auth.py``` file to define an Authentication Manager. If using JWT make sure its python package is installed.

  - User
    Within this package create an ```user.py``` file to define User available actions such as Register, Login or Logout.
    To hash user's password, we will need to install ```passlib``` to use one of its methods.

    ```pip install passlib```

    ```python
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    class UserManager:
    @staticmethod
    async def register(user_data):
        user_data["password"] = pwd_context.hash(user_data["password"])
    ```

- Schemas
Create a ```schemas``` package, which will contain at least two more packages, one called ```request``` and the other one ```response```.

Under the ```request``` package create a ```user.py``` file where we will create the User behavior when Registering and Logging In as UserBase class(es).

```python
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserRegisterIn(UserBase):
    password: str
    phone: str
    first_name: str
    last_name: str
    iban: str

class UserLoginIn(UserBase):
    password: str
```

After creating our schemas we would need to reference them in our resource.auth.py file, where the ```user_data``` will be of these schemas type as follows:

```python
from schemas.request.user import UserRegisterIn, UserLoginIn

@router.post("/register/", status_code=201)
async def register(user_data: UserRegisterIn):
    token = await UserManager.register(user_data)
    return {"token": token}


@router.post("/login/")
async def login(user_data: UserLoginIn):
    token = await UserManager.login(user_data)
    return {"token": token}
```


## Login

On ```managers.user``` we will add a method to handle our App Login.

## Complaint

Create a file within the ```managers``` package calles ```complaint.py```.
Also create a file ```complaint.py``` on the ```schemas.request``` and ```schemas.response```packages.

## Super USer

Install ```asyncclick``` and then create a package called ```commands```. Inside this package create a file called ```create_super_user```.

The whole script should look something like this:
```python
import asyncclick as click


from models.enums import RoleType
from db import database
from managers.user import UserManager


@click.command()
@click.option("-f", "--first_name", type=str, required=True)
@click.option("-l", "--last_name", type=str, required=True)
@click.option("-e", "--email", type=str, required=True)
@click.option("-p", "--phone", type=str, required=True)
@click.option("-i", "--iban", type=str, required=True)
@click.option("-pa", "--password", type=str, required=True)
async def create_user(first_name, last_name, email, phone, iban, password):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "iban": iban,
        "password": password,
        "role": RoleType.admin
    }
    await database.connect()
    await UserManager.register(user_data)
    await database.disconnect()


if __name__ == "__main__":
    create_user(_anyio_backend="asyncio")
```

We will import ```asyncclick``` used for the ```.command```, ```.option``` and ```_anyio_backend="asyncio"```
```python
import asyncclick as click

@click.command()
@click.option("-f", "--first_name", type=str, required=True)
#...

if __name__ == "__main__":
    create_user(_anyio_backend="asyncio")
```

The ```.command``` and ```.option``` commands will allow us to set parameters when creating the super user account:
```python
@click.command()
@click.option("-f", "--first_name", type=str, required=True)
@click.option("-l", "--last_name", type=str, required=True)
@click.option("-e", "--email", type=str, required=True)
@click.option("-p", "--phone", type=str, required=True)
@click.option("-i", "--iban", type=str, required=True)
@click.option("-pa", "--password", type=str, required=True)
```

These decorators will be used to decorate a function where we assign the user data values and then proceed to write them in the database:
```python
async def create_user(first_name, last_name, email, phone, iban, password):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "iban": iban,
        "password": password,
        "role": RoleType.admin
    }
    await database.connect()
    await UserManager.register(user_data)
    await database.disconnect()
```

Finally on a bash command line execute the following:
```
export PYTHONPATH=./

python commands/create_super_user.py -f John -l Doe -e admin@mail.com -p 4421234567 -i GB29NWBK60161331926819 -pa pass123
```