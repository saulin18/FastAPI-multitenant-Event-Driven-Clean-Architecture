
### App multi tenant with Clean Architecture and Event Driven Architecture

For now we have the tenant endpoints, users and the base of the architecture. It will probably change in the future.

Look at the .env.example file for an example of the environment variables. You also have the settings.py at app/shared/config.py for the default settings.

We use resend for sending emails.

### For configuring resend, look here: https://resend.mintlify.dev/docs/send-with-python

For dev I recommend docker, just `docker compose up` and when you finish `docker compose down`.

For installing dependencies use poetry: `poetry install`

For running the app go `cd app` and then `py main.py` (Python 3.11)

## The architecture

**/api**

API layer, all HTTP calls, endpoints, middlewares, etc.

**/domain**

Core logic of the business, entities, domain events, domain exceptions, interfaces (there are interfaces that shouldn't be part of the domain). Here don't live the implementations, is pure business logic.

**/infrastructure**

Concrete implementations, databases, implement the domain interfaces, authentication, external services, storages, etc. Depends on domain and can depend on application layer for DTOs and other stuffs.

**/application**

Use cases, handlers, pagination, data transformation for sending to the user if it's necessary, is the layer that orchestrates everything and receives the components (repositories, services) via dependency injection. DON'T RECEIVE CONCRETE IMPLEMENTATIONS, only interfaces for ensuring decoupling.

**/ioc**

Inversion of control, is the glue of the architecture. Ensures decoupling and consistency, using Python dependency injector.

**/shared**

Shared between all layers.

## Database Migrations

We use Alembic for creating migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>

# Show current revision
alembic current

# Show migration history
alembic history
```