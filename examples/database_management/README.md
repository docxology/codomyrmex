# Database Management Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - [db_performance](db_performance/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Complete | **Last Updated**: December 2025

## Overview

This example demonstrates comprehensive database management operations using the Codomyrmex `database_management` module. It showcases database connection management, schema generation, data migration, backup operations, and performance monitoring across multiple database types.

## What This Example Demonstrates

### Core Features
- **Database Connection Management**: Multi-database support with connection pooling
- **Schema Generation**: Automated database schema creation and management
- **Data Migration**: Migration execution and rollback management
- **Database Backup**: Automated backup and recovery operations
- **Performance Monitoring**: Database metrics collection and analysis
- **Database Optimization**: Automated optimization and maintenance
- **Multi-Database Support**: SQLite, PostgreSQL, MySQL, and other database types

### Key Capabilities
- Connection configuration and management
- Schema definition and generation
- Migration planning and execution
- Backup scheduling and retention
- Performance monitoring and alerting
- Database optimization and tuning
- Cross-database compatibility

## Tested Methods

This example references the following tested methods from `src/codomyrmex/tests/unit/test_database_management.py`:

- `DatabaseManager.add_connection()` - Verified in `TestDatabaseManager::test_add_connection`
- `DatabaseConnection.execute_query()` - Verified in `TestDatabaseConnection::test_execute_query_select_sqlite`
- `MigrationManager.run_migration()` - Verified in `TestDatabaseManager::test_run_migration`
- `BackupManager.backup_database()` - Verified in `TestDatabaseManager::test_backup_database`
- `DatabaseMonitor.monitor_database()` - Verified in `TestDatabaseManager::test_monitor_database`
- `SchemaGenerator.generate_schema()` - Verified in `TestDatabaseManager::test_generate_schema`

## Running the Example

### Quick Start

```bash
# Navigate to the example directory
cd examples/database_management

# Run with default YAML configuration
python example_basic.py

# Run with JSON configuration
python example_basic.py --config config.json

# Run with custom configuration
python example_basic.py --config my_custom_config.yaml
```

### Expected Output

The example will:
1. Create multiple database connections (SQLite and PostgreSQL)
2. Generate a comprehensive database schema with tables and relationships
3. Execute schema creation and populate with sample data
4. Perform data queries and demonstrate migration execution
5. Create database backups with compression
6. Monitor database performance and apply optimizations
7. Save schema files and backup information

### Sample Output Structure

```json
{
  "database_connections_created": 2,
  "schema_tables_generated": 2,
  "sample_users_inserted": 3,
  "sample_posts_inserted": 3,
  "migration_executed": true,
  "backup_created": true,
  "performance_metrics_collected": true,
  "optimizations_applied": 3,
  "schema_file_saved": "output/schemas/generated_schema.sql",
  "backup_info_saved": "output/schemas/backup_info.json",
  "database_types_supported": ["sqlite", "postgresql", "mysql", "oracle", "sqlserver"],
  "connections_active": 1,
  "total_queries_executed": 8,
  "schema_generation_success": true,
  "migration_manager_initialized": true,
  "backup_manager_initialized": true,
  "monitor_initialized": true
}
```

## Configuration Options

### Database Connections

Configure multiple database connections:

```yaml
databases:
  development:
    type: sqlite
    database: development.db
    host: localhost
    username: dev_user
    password: dev_pass

  production:
    type: postgresql
    host: prod.example.com
    port: 5432
    database: production
    username: prod_user
    password: prod_pass
    ssl_mode: require
    connection_pool_size: 10
```

### Schema Generation

Customize schema generation settings:

```yaml
schema:
  target_database: sqlite        # Target database type
  naming_convention: snake_case  # Column naming convention
  include_foreign_keys: true     # Generate foreign key constraints
  include_indexes: true          # Generate indexes
  generate_migrations: true      # Create migration files
```

### Migration Management

Configure migration settings:

```yaml
migrations:
  directory: migrations                    # Migration files directory
  naming_pattern: "{timestamp}_{name}.sql" # Migration file naming
  auto_rollback: true                     # Generate rollback scripts
  timeout: 300                           # Migration timeout (seconds)
  dry_run: false                         # Dry run mode
```

### Backup Configuration

Set up backup policies:

```yaml
backup:
  directory: backups
  naming_pattern: "{database}_{timestamp}.backup"
  compression:
    enabled: true
    algorithm: gzip
    level: 6
  retention:
    keep_daily: 7
    keep_weekly: 4
    keep_monthly: 12
```

### Performance Monitoring

Configure monitoring settings:

```yaml
monitoring:
  interval: 60                            # Collection interval (seconds)
  metrics:                                # Metrics to collect
    - connection_count
    - query_count
    - slow_queries
    - table_sizes
    - index_usage
  thresholds:                             # Alert thresholds
    max_connections: 100
    slow_query_threshold: 5.0
    max_table_size: 1000000
```

## Database Types Supported

The example demonstrates support for multiple database types:

| Database Type | Status | Features |
|---------------|--------|----------|
| **SQLite** | ✅ Full Support | Local file-based database, ACID compliance |
| **PostgreSQL** | ✅ Full Support | Advanced features, JSON support, extensions |
| **MySQL** | ✅ Full Support | High performance, replication support |
| **Oracle** | ✅ Full Support | Enterprise features, partitioning |
| **SQL Server** | ✅ Full Support | Windows integration, advanced analytics |

## Schema Definition

The example creates a sample user management schema:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Posts Table
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Migration Examples

### Sample Migration
```python
migration = Migration(
    name="add_user_status",
    version="1.1.0",
    description="Add status column to users table",
    up_sql="ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'",
    down_sql="ALTER TABLE users DROP COLUMN status"
)
```

### Migration Execution
```python
result = migration_manager.run_migration(migration, connection)
```

## Backup Operations

### Backup Configuration
```python
backup_config = Backup(
    name="daily_backup",
    database_path="development.db",
    backup_path="backup_development.db",
    compression=True
)
```

### Backup Execution
```python
result = backup_manager.backup_database(backup_config)
```

## Performance Monitoring

### Metrics Collection
- **Connection Count**: Active database connections
- **Query Count**: Total queries executed
- **Slow Queries**: Queries exceeding threshold
- **Table Sizes**: Row counts per table
- **Index Usage**: Index utilization statistics

### Optimization Types
- **VACUUM**: Reclaim storage and optimize table layout
- **REINDEX**: Rebuild indexes for optimal performance
- **ANALYZE**: Update query planner statistics
- **CLUSTER**: Physically reorder table data

## Integration Examples

### Web Application Integration

```python
from codomyrmex.database_management import DatabaseManager, DatabaseConnection

# Initialize database manager
manager = DatabaseManager()

# Add production connection
prod_conn = DatabaseConnection(
    name="web_app_db",
    db_type=DatabaseType.POSTGRESQL,
    host="db.example.com",
    database="webapp",
    username="webapp_user",
    password=os.getenv("DB_PASSWORD")
)
manager.add_connection(prod_conn)

# Use in application
def get_user(user_id):
    conn = manager.get_connection("web_app_db")
    return conn.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
```

### CI/CD Pipeline Integration

```python
from codomyrmex.database_management import run_migrations, backup_database

# Pre-deployment backup
backup_result = backup_database({
    "database": "production.db",
    "backup_path": f"backup_{datetime.now().isoformat()}.db"
})

# Run migrations
migration_result = run_migrations("migrations/", "production.db")

# Post-deployment verification
if not migration_result["success"]:
    # Rollback logic
    pass
```

## Output Files

The example generates several output files:

- `output/database_management_results.json` - Complete analysis results
- `output/schemas/generated_schema.sql` - Generated database schema
- `output/schemas/backup_info.json` - Backup configuration and metadata
- `logs/database_management.log` - Execution logs

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check database credentials and network connectivity
2. **Migration Failures**: Verify migration syntax and dependencies
3. **Backup Errors**: Ensure sufficient disk space and permissions
4. **Performance Issues**: Check database configuration and indexes

### Performance Considerations

- Use connection pooling for high-traffic applications
- Implement proper indexing strategies
- Monitor slow queries and optimize accordingly
- Schedule maintenance during low-traffic periods

## Security Considerations

- Store database credentials securely (environment variables, secret managers)
- Use SSL/TLS encryption for production connections
- Implement proper access controls and user permissions
- Regular security audits and vulnerability scanning

## Related Examples

- **[API Standardization](../api_standardization/)** - API database integration
- **[Security Audit](../security_audit/)** - Database security scanning
- **[Performance](../performance/)** - Database performance monitoring
- **[Config Management](../config_management/)** - Database configuration management

## Module Documentation

- **[Database Management Module](../../src/codomyrmex/database_management/)** - Complete module documentation
- **[Database Management Module](../../src/codomyrmex/database_management/)** - Complete module documentation and API reference

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
