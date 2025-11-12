# Database Setup Instructions

## Problem
The application requires a PostgreSQL database with the following credentials:
- Database: `integration_db`
- User: `integration_user`
- Password: `integration_pass`
- Host: `localhost`
- Port: `5432`

## Solution Options

### Option 1: Using Docker Compose (Recommended)
If you have Docker installed, you can use docker-compose to set up the database:

```bash
docker-compose up -d postgres redis
```

This will automatically create the database and user with the correct credentials.

### Option 2: Manual Setup
If PostgreSQL is already running locally, create the database and user manually:

```bash
# Connect to PostgreSQL as the postgres superuser
sudo -u postgres psql

# Then run these SQL commands:
CREATE USER integration_user WITH PASSWORD 'integration_pass';
CREATE DATABASE integration_db OWNER integration_user;
GRANT ALL PRIVILEGES ON DATABASE integration_db TO integration_user;
\q
```

### Option 3: Using psql directly
If you have access to the postgres user without sudo:

```bash
psql -U postgres -c "CREATE USER integration_user WITH PASSWORD 'integration_pass';"
psql -U postgres -c "CREATE DATABASE integration_db OWNER integration_user;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE integration_db TO integration_user;"
```

## Verify Setup
After setting up the database, verify the connection:

```bash
PGPASSWORD=integration_pass psql -h localhost -U integration_user -d integration_db -c "SELECT 1;"
```

If this command succeeds, the database is set up correctly.

## After Database Setup
1. Restart the backend service to initialize database tables
2. The circuit breaker will automatically reset after 60 seconds, or you can restart the backend

## Troubleshooting

### "password authentication failed"
- The user doesn't exist or the password is incorrect
- Run the CREATE USER command again

### "database does not exist"
- The database hasn't been created
- Run the CREATE DATABASE command

### "permission denied"
- The user doesn't have the necessary privileges
- Run the GRANT command again


