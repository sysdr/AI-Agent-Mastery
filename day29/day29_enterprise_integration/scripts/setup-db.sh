#!/bin/bash

echo "🔧 Setting up PostgreSQL database..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Try to connect as postgres user (may require password)
echo "Creating database user and database..."
echo "Note: This may require sudo or postgres user password"

# Create user (if it doesn't exist)
sudo -u postgres psql -c "CREATE USER integration_user WITH PASSWORD 'integration_pass';" 2>/dev/null || \
    echo "User may already exist or requires manual creation"

# Create database (if it doesn't exist)
sudo -u postgres psql -c "CREATE DATABASE integration_db OWNER integration_user;" 2>/dev/null || \
    echo "Database may already exist or requires manual creation"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE integration_db TO integration_user;" 2>/dev/null || \
    echo "Privileges may already be granted or requires manual setup"

echo ""
echo "✅ Database setup complete!"
echo ""
echo "If the above commands failed, please run manually:"
echo "  sudo -u postgres psql"
echo "  CREATE USER integration_user WITH PASSWORD 'integration_pass';"
echo "  CREATE DATABASE integration_db OWNER integration_user;"
echo "  GRANT ALL PRIVILEGES ON DATABASE integration_db TO integration_user;"
echo "  \\q"


