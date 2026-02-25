# Testing Module - API Specification

## Overview

The Testing module provides test fixtures, generators, and utilities for the Codomyrmex test suite. It includes two submodules: `fixtures` for test fixture management and `generators` for test data generation.

## Submodules

### fixtures

Test fixture management and setup utilities.

### generators

Test data generation utilities.

---

## fixtures Submodule

### Classes

#### FixtureScope

Enumeration of fixture scopes.

```python
from codomyrmex.testing.fixtures import FixtureScope

# Values
FixtureScope.FUNCTION   # Per-function scope
FixtureScope.CLASS      # Per-class scope
FixtureScope.MODULE     # Per-module scope
FixtureScope.SESSION    # Per-session scope
```

#### FixtureDefinition

Data class representing a fixture definition.

```python
from codomyrmex.testing.fixtures import FixtureDefinition

definition = FixtureDefinition(
    name="db",
    factory=create_test_db,
    scope=FixtureScope.MODULE,
    cleanup=lambda db: db.close(),
    dependencies=["config"]
)
```

**Attributes:**
- `name: str` - Fixture name
- `factory: Callable[[], Any]` - Factory function to create fixture
- `scope: FixtureScope` - Fixture scope (default: FUNCTION)
- `cleanup: Optional[Callable[[Any], None]]` - Cleanup function
- `dependencies: List[str]` - List of dependent fixture names

#### FixtureInstance

Data class representing an instantiated fixture.

```python
from codomyrmex.testing.fixtures import FixtureInstance

# Attributes
instance.name        # str: Fixture name
instance.value       # Any: The fixture value
instance.scope       # FixtureScope: The scope
instance.created_at  # datetime: When created
```

#### FixtureManager

Manages test fixtures with dependency resolution and cleanup.

```python
from codomyrmex.testing.fixtures import FixtureManager

fixtures = FixtureManager()

# Register fixtures
fixtures.register("db", lambda: create_test_db())
fixtures.register(
    "user",
    lambda: create_test_user(),
    cleanup=lambda u: u.delete()
)

# Use fixtures
with fixtures.use("db") as db:
    # test with db
    pass

# Manual get/cleanup
value = fixtures.get("db")
fixtures.cleanup("db")
fixtures.cleanup_all()

# List fixtures
names = fixtures.list_fixtures()
```

**Methods:**
- `register(name, factory, scope, cleanup, dependencies)` - Register a fixture
- `get(name) -> Any` - Get or create fixture instance
- `cleanup(name)` - Clean up specific fixture
- `cleanup_all()` - Clean up all fixtures
- `use(name)` - Context manager for fixture usage
- `list_fixtures() -> List[str]` - List registered fixture names

#### DataFixture

Pre-defined data fixture with filtering capabilities.

```python
from codomyrmex.testing.fixtures import DataFixture

users = DataFixture([
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
])

# Access
assert users[0]["name"] == "Alice"
assert len(users) == 2

# Filter
active = users.filter(active=True)
bob = users.find(id=2)
all_users = users.all()

# Iterate
for user in users:
    print(user["name"])
```

**Methods:**
- `__getitem__(index) -> Dict[str, Any]` - Access by index
- `__len__() -> int` - Get count
- `__iter__()` - Iterate over records
- `filter(**kwargs) -> List[Dict[str, Any]]` - Filter by field values
- `find(**kwargs) -> Optional[Dict[str, Any]]` - Find first match
- `all() -> List[Dict[str, Any]]` - Get all records

#### JSONFixtureLoader

Loads fixtures from JSON files with caching.

```python
from codomyrmex.testing.fixtures import JSONFixtureLoader

loader = JSONFixtureLoader("tests/fixtures")
users = loader.load("users")  # Loads users.json
loader.clear_cache()
```

**Methods:**
- `load(name) -> DataFixture` - Load fixture by name
- `clear_cache()` - Clear loaded fixture cache

#### FixtureBuilder

Fluent builder for creating fixture data.

```python
from codomyrmex.testing.fixtures import FixtureBuilder

user = (FixtureBuilder("user")
    .with_field("id", 1)
    .with_field("name", "Test User")
    .with_field("active", True)
    .build())

# Or multiple fields at once
item = (FixtureBuilder("item")
    .with_fields(a=1, b=2, c=3)
    .build())

# Build many with incremental IDs
users = (FixtureBuilder("user")
    .with_field("name", "User")
    .build_many(10))  # Creates 10 users with id=1..10
```

**Methods:**
- `with_field(key, value) -> FixtureBuilder` - Add single field
- `with_fields(**kwargs) -> FixtureBuilder` - Add multiple fields
- `build() -> Dict[str, Any]` - Build single fixture
- `build_many(count, id_field="id") -> List[Dict[str, Any]]` - Build many with IDs

---

## generators Submodule

### Classes

#### DataType

Enumeration of data types for generation.

```python
from codomyrmex.testing.generators import DataType

# Values
DataType.STRING
DataType.INTEGER
DataType.FLOAT
DataType.BOOLEAN
DataType.DATE
DataType.EMAIL
DataType.UUID
DataType.NAME
DataType.ADDRESS
DataType.PHONE
```

#### FieldSpec

Specification for a generated field.

```python
from codomyrmex.testing.generators import FieldSpec, DataType

spec = FieldSpec(
    name="age",
    data_type=DataType.INTEGER,
    nullable=False,
    unique=True,
    min_value=18,
    max_value=100
)
```

#### Generator (Abstract Base)

Base class for all data generators.

```python
from codomyrmex.testing.generators import Generator

class MyGenerator(Generator):
    def generate(self) -> Any:
        return "custom_value"

gen = MyGenerator()
value = gen.generate()
values = gen.generate_many(10)
```

#### StringGenerator

Generates random strings.

```python
from codomyrmex.testing.generators import StringGenerator

gen = StringGenerator(
    min_length=5,
    max_length=20,
    charset="abc123"  # Optional custom charset
)
result = gen.generate()
```

#### IntegerGenerator

Generates random integers.

```python
from codomyrmex.testing.generators import IntegerGenerator

gen = IntegerGenerator(min_value=0, max_value=1000)
result = gen.generate()
```

#### FloatGenerator

Generates random floats with precision control.

```python
from codomyrmex.testing.generators import FloatGenerator

gen = FloatGenerator(
    min_value=0.0,
    max_value=100.0,
    precision=2
)
result = gen.generate()  # e.g., 42.57
```

#### BooleanGenerator

Generates random booleans with configurable probability.

```python
from codomyrmex.testing.generators import BooleanGenerator

gen = BooleanGenerator(true_probability=0.7)
result = gen.generate()
```

#### DateGenerator

Generates random dates within a range.

```python
from codomyrmex.testing.generators import DateGenerator
from datetime import datetime

gen = DateGenerator(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2025, 12, 31)
)
result = gen.generate()
```

#### EmailGenerator

Generates random email addresses.

```python
from codomyrmex.testing.generators import EmailGenerator

gen = EmailGenerator()
result = gen.generate()  # e.g., "xkjfh@example.com"
```

#### UUIDGenerator

Generates UUID-like strings.

```python
from codomyrmex.testing.generators import UUIDGenerator

gen = UUIDGenerator()
result = gen.generate()  # e.g., "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
```

#### NameGenerator

Generates random full names.

```python
from codomyrmex.testing.generators import NameGenerator

gen = NameGenerator()
result = gen.generate()  # e.g., "Alice Smith"
```

#### ChoiceGenerator

Generates random choice from a list.

```python
from codomyrmex.testing.generators import ChoiceGenerator

gen = ChoiceGenerator(["red", "green", "blue"])
result = gen.generate()  # e.g., "green"
```

#### RecordGenerator

Generates structured records with multiple fields.

```python
from codomyrmex.testing.generators import (
    RecordGenerator,
    NameGenerator,
    EmailGenerator,
    IntegerGenerator
)

gen = RecordGenerator()
gen.add_field("name", NameGenerator())
gen.add_field("email", EmailGenerator())
gen.add_field("age", IntegerGenerator(18, 65))

record = gen.generate()
records = gen.generate_many(100)
```

**Methods:**
- `add_field(name, generator) -> RecordGenerator` - Add field generator
- `generate() -> Dict[str, Any]` - Generate single record
- `generate_many(count) -> List[Dict[str, Any]]` - Generate multiple records

#### DatasetGenerator

Generates complete datasets with multiple columns.

```python
from codomyrmex.testing.generators import (
    DatasetGenerator,
    UUIDGenerator,
    NameGenerator,
    BooleanGenerator
)

dataset = DatasetGenerator("users")
dataset.add_column("id", UUIDGenerator())
dataset.add_column("name", NameGenerator())
dataset.add_column("active", BooleanGenerator())

data = dataset.generate(rows=1000)
csv = dataset.generate_csv(rows=100)
columns = dataset.columns  # ["id", "name", "active"]
```

**Methods:**
- `add_column(name, generator) -> DatasetGenerator` - Add column generator
- `columns -> List[str]` - Get column names
- `generate(rows=100) -> List[Dict[str, Any]]` - Generate dataset
- `generate_csv(rows=100) -> str` - Generate as CSV string

---

## Usage Examples

### Creating Test Fixtures

```python
from codomyrmex.testing.fixtures import FixtureManager, FixtureScope

# Set up fixture manager
fixtures = FixtureManager()

# Register database fixture with module scope
fixtures.register(
    "db",
    lambda: connect_to_test_db(),
    scope=FixtureScope.MODULE,
    cleanup=lambda db: db.close()
)

# Register user fixture depending on db
fixtures.register(
    "test_user",
    lambda: create_user(fixtures.get("db")),
    dependencies=["db"],
    cleanup=lambda u: u.delete()
)

# Use in tests
def test_user_creation():
    with fixtures.use("test_user") as user:
        assert user.id is not None
```

### Generating Test Data

```python
from codomyrmex.testing.generators import (
    DatasetGenerator,
    UUIDGenerator,
    NameGenerator,
    EmailGenerator,
    IntegerGenerator,
    BooleanGenerator,
    DateGenerator
)

# Create user dataset generator
users = DatasetGenerator("users")
users.add_column("id", UUIDGenerator())
users.add_column("name", NameGenerator())
users.add_column("email", EmailGenerator())
users.add_column("age", IntegerGenerator(18, 80))
users.add_column("active", BooleanGenerator(true_probability=0.9))
users.add_column("created", DateGenerator())

# Generate 1000 test users
test_data = users.generate(rows=1000)

# Or export as CSV for external tools
csv_data = users.generate_csv(rows=1000)
```

### Loading JSON Fixtures

```python
from codomyrmex.testing.fixtures import JSONFixtureLoader

# Load fixtures from tests/fixtures directory
loader = JSONFixtureLoader("tests/fixtures")

# Load users.json
users = loader.load("users")

# Filter and find
admins = users.filter(role="admin")
alice = users.find(name="Alice")
```

---

## Module Exports

### fixtures

```python
__all__ = [
    "FixtureScope",
    "FixtureDefinition",
    "FixtureInstance",
    "FixtureManager",
    "DataFixture",
    "JSONFixtureLoader",
    "FixtureBuilder",
]
```

### generators

```python
__all__ = [
    "DataType",
    "FieldSpec",
    "Generator",
    "StringGenerator",
    "IntegerGenerator",
    "FloatGenerator",
    "BooleanGenerator",
    "DateGenerator",
    "EmailGenerator",
    "UUIDGenerator",
    "NameGenerator",
    "ChoiceGenerator",
    "RecordGenerator",
    "DatasetGenerator",
]
```
