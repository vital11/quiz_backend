# Using Asyncio with Alembic

```shell
# Initialize Alembic
alembic init -t async <script_directory_here>
```

# Data Migrations

```shell
# Create and Apply Migrations
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
alembic downgrade -1
```
