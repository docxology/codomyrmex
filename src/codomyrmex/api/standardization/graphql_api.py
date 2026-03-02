import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""GraphQL API Implementation for Codomyrmex

This module provides a GraphQL API framework with schema generation,
resolvers, mutations, and query optimization.
"""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class GraphQLType(Enum):
    """GraphQL type definitions."""
    STRING = "String"
    INT = "Int"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    ID = "ID"

@dataclass
class GraphQLField:
    """Represents a GraphQL field definition."""
    name: str
    type: Union[str, 'GraphQLObjectType']
    description: str | None = None
    args: dict[str, Union[str, 'GraphQLObjectType']] = field(default_factory=dict)
    resolver: Callable | None = None
    required: bool = False

@dataclass
class GraphQLObjectType:
    """Represents a GraphQL object type."""
    name: str
    fields: dict[str, GraphQLField] = field(default_factory=dict)
    description: str | None = None
    interfaces: list[str] = field(default_factory=list)

    def add_field(self, field: GraphQLField) -> None:
        """Add a field to the object type."""
        self.fields[field.name] = field

    def get_field(self, name: str) -> GraphQLField | None:
        """Get a field by name."""
        return self.fields.get(name)

@dataclass
class GraphQLSchema:
    """GraphQL schema definition."""
    query_type: GraphQLObjectType | None = None
    mutation_type: GraphQLObjectType | None = None
    subscription_type: GraphQLObjectType | None = None
    types: dict[str, GraphQLObjectType] = field(default_factory=dict)

    def add_type(self, type_def: GraphQLObjectType) -> None:
        """Add a type to the schema."""
        self.types[type_def.name] = type_def

    def get_type(self, name: str) -> GraphQLObjectType | None:
        """Get a type by name."""
        return self.types.get(name)

    def generate_sdl(self) -> str:
        """
        Generate GraphQL Schema Definition Language (SDL).

        Returns:
            SDL string
        """
        lines = []

        # Add types
        for type_name, type_def in self.types.items():
            lines.append(f"type {type_name} {{")
            for field_name, field_def in type_def.fields.items():
                field = field_def
                args_str = ""
                if field.args:
                    args_list = []
                    for arg_name, arg_type in field.args.items():
                        arg_type_str = arg_type if isinstance(arg_type, str) else arg_type.name
                        args_list.append(f"{arg_name}: {arg_type_str}")
                    args_str = f"({', '.join(args_list)})"

                field_type_str = field.type if isinstance(field.type, str) else field.type.name
                required_marker = "!" if field.required else ""
                lines.append(f"  {field_name}{args_str}: {field_type_str}{required_marker}")
            lines.append("}")

        # Add Query type
        if self.query_type:
            lines.append("type Query {")
            for field_name, field in self.query_type.fields.items():
                args_str = ""
                if field.args:
                    args_list = []
                    for arg_name, arg_type in field.args.items():
                        arg_type_str = arg_type if isinstance(arg_type, str) else arg_type.name
                        args_list.append(f"{arg_name}: {arg_type_str}")
                    args_str = f"({', '.join(args_list)})"

                field_type_str = field.type if isinstance(field.type, str) else field.type.name
                required_marker = "!" if field.required else ""
                lines.append(f"  {field_name}{args_str}: {field_type_str}{required_marker}")
            lines.append("}")

        # Add Mutation type
        if self.mutation_type:
            lines.append("type Mutation {")
            for field_name, field in self.mutation_type.fields.items():
                args_str = ""
                if field.args:
                    args_list = []
                    for arg_name, arg_type in field.args.items():
                        arg_type_str = arg_type if isinstance(arg_type, str) else arg_type.name
                        args_list.append(f"{arg_name}: {arg_type_str}")
                    args_str = f"({', '.join(args_list)})"

                field_type_str = field.type if isinstance(field.type, str) else field.type.name
                required_marker = "!" if field.required else ""
                lines.append(f"  {field_name}{args_str}: {field_type_str}{required_marker}")
            lines.append("}")

        return "\n".join(lines)

@dataclass
class GraphQLResolver:
    """GraphQL resolver for handling field resolution."""
    field_name: str
    resolver_func: Callable
    complexity: int = 1

    def resolve(self, parent: Any, args: dict[str, Any], context: dict[str, Any]) -> Any:
        """
        Resolve the field value.

        Args:
            parent: Parent object
            args: Field arguments
            context: Resolution context

        Returns:
            Resolved value
        """
        try:
            return self.resolver_func(parent, args, context)
        except Exception as e:
            logger.error(f"Resolver error for field {self.field_name}: {e}")
            raise

@dataclass
class GraphQLMutation:
    """GraphQL mutation definition."""
    name: str
    input_type: GraphQLObjectType
    output_type: str | GraphQLObjectType
    resolver: Callable
    description: str | None = None

    def execute(self, input_data: dict[str, Any], context: dict[str, Any]) -> Any:
        """
        Execute the mutation.

        Args:
            input_data: Mutation input data
            context: Execution context

        Returns:
            Mutation result
        """
        try:
            return self.resolver(input_data, context)
        except Exception as e:
            logger.error(f"Mutation error for {self.name}: {e}")
            raise

@dataclass
class GraphQLQuery:
    """GraphQL query representation."""
    operation: str  # 'query', 'mutation', or 'subscription'
    selection_set: dict[str, Any]
    variables: dict[str, Any] = field(default_factory=dict)
    operation_name: str | None = None

class GraphQLAPI:
    """
    Main GraphQL API class for handling GraphQL requests.
    """

    def __init__(self, schema: GraphQLSchema):
        """
        Initialize the GraphQL API.

        Args:
            schema: GraphQL schema
        """
        self.schema = schema
        self.resolvers: dict[str, dict[str, GraphQLResolver]] = {}
        self.mutations: dict[str, GraphQLMutation] = {}
        self.query_complexity_limit = 1000
        self.request_count = 0
        self.error_count = 0

        # Register built-in resolvers
        self._register_builtin_resolvers()

        logger.info("GraphQL API initialized")

    def register_resolver(self, type_name: str, field_name: str,
                         resolver: GraphQLResolver) -> None:
        """
        Register a field resolver.

        Args:
            type_name: Type name
            field_name: Field name
            resolver: Resolver instance
        """
        if type_name not in self.resolvers:
            self.resolvers[type_name] = {}

        self.resolvers[type_name][field_name] = resolver
        logger.debug(f"Registered resolver: {type_name}.{field_name}")

    def register_mutation(self, mutation: GraphQLMutation) -> None:
        """
        Register a mutation.

        Args:
            mutation: Mutation to register
        """
        self.mutations[mutation.name] = mutation
        logger.debug(f"Registered mutation: {mutation.name}")

    def execute_query(self, query: str, variables: dict[str, Any] | None = None,
                     context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            context: Execution context

        Returns:
            Query result
        """
        self.request_count += 1

        try:
            # Parse query (simplified - in real implementation, use a proper GraphQL parser)
            parsed_query = self._parse_query(query)

            # Validate query complexity
            complexity = self._calculate_complexity(parsed_query)
            if complexity > self.query_complexity_limit:
                raise ValueError(f"Query complexity {complexity} exceeds limit {self.query_complexity_limit}")

            # Execute query
            result = self._execute_operation(parsed_query, variables or {}, context or {})

            return {"data": result}

        except Exception as e:
            self.error_count += 1
            logger.error(f"Query execution error: {e}")
            return {"errors": [{"message": str(e)}]}

    def _parse_query(self, query: str) -> GraphQLQuery:
        """
        Parse a GraphQL query string (simplified implementation).

        Args:
            query: GraphQL query string

        Returns:
            Parsed query object
        """
        # This is a very simplified parser - in production, use a proper GraphQL parser
        # For now, we'll assume a basic structure
        operation = "query"
        if "mutation" in query.lower():
            operation = "mutation"

        # Extract operation name if present
        operation_name = None
        if "{" in query:
            before_brace = query.split("{")[0].strip()
            if before_brace.startswith(("query", "mutation")):
                parts = before_brace.split()
                if len(parts) > 1:
                    operation_name = parts[1]

        return GraphQLQuery(
            operation=operation,
            selection_set={},  # Would parse actual selection set
            operation_name=operation_name
        )

    def _calculate_complexity(self, query: GraphQLQuery) -> int:
        """
        Calculate query complexity.

        Args:
            query: Parsed query

        Returns:
            Complexity score
        """
        # Simplified complexity calculation
        return 1

    def _execute_operation(self, query: GraphQLQuery, variables: dict[str, Any],
                          context: dict[str, Any]) -> Any:
        """
        Execute a GraphQL operation.

        Args:
            query: Parsed query
            variables: Query variables
            context: Execution context

        Returns:
            Execution result
        """
        if query.operation == "query" and self.schema.query_type:
            return self._execute_selection_set(self.schema.query_type, {}, context)
        elif query.operation == "mutation":
            # Handle mutations
            return {}

        return {}

    def _execute_selection_set(self, object_type: GraphQLObjectType, parent: Any,
                              context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a selection set against an object type.

        Args:
            object_type: Object type to execute against
            parent: Parent object
            context: Execution context

        Returns:
            Result dictionary
        """
        result = {}

        for field_name, field_def in object_type.fields.items():
            field = field_def
            if field.resolver:
                # Use custom resolver
                try:
                    value = field.resolver(parent, {}, context)
                except Exception as e:
                    logger.error(f"Field resolution error for {field_name}: {e}")
                    value = None
            else:
                # Default field resolution
                value = getattr(parent, field_name, None)

            result[field_name] = value

        return result

    def _register_builtin_resolvers(self) -> None:
        """Register built-in resolvers for common types."""
        # Functional base implementation registering universal __typename
        self.register_resolver("__Any", "__typename",
                               GraphQLResolver("__typename", lambda p, a, c: type(p).__name__))

    def get_schema_sdl(self) -> str:
        """
        Get the GraphQL schema as SDL.

        Returns:
            Schema SDL string
        """
        return self.schema.generate_sdl()

    def get_metrics(self) -> dict[str, Any]:
        """
        Get API metrics.

        Returns:
            Dictionary with API metrics
        """
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "registered_resolvers": sum(len(resolvers) for resolvers in self.resolvers.values()),
            "registered_mutations": len(self.mutations)
        }

    def validate_query(self, query: str) -> list[str]:
        """
        Validate a GraphQL query.

        Args:
            query: GraphQL query string

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            self._parse_query(query)
            # Add validation logic here
        except Exception as e:
            errors.append(str(e))

        return errors

# Decorator for GraphQL resolvers
def resolver(field_name: str, complexity: int = 1):
    """
    Decorator to mark functions as GraphQL resolvers.

    Args:
        field_name: Name of the field this resolver handles
        complexity: Query complexity cost

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> GraphQLResolver:
        """Decorator."""

        return GraphQLResolver(
            field_name=field_name,
            resolver_func=func,
            complexity=complexity
        )
    return decorator

# Decorator for GraphQL mutations
def mutation(name: str, input_type: GraphQLObjectType,
             output_type: str | GraphQLObjectType, description: str | None = None):
    """
    Decorator to mark functions as GraphQL mutations.

    Args:
        name: Mutation name
        input_type: Input type for the mutation
        output_type: Output type for the mutation
        description: Mutation description

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> GraphQLMutation:
        """Decorator."""

        return GraphQLMutation(
            name=name,
            input_type=input_type,
            output_type=output_type,
            resolver=func,
            description=description
        )
    return decorator

# Convenience functions
def create_schema() -> GraphQLSchema:
    """
    Create a new GraphQL schema.

    Returns:
        GraphQLSchema instance
    """
    return GraphQLSchema()

def create_object_type(name: str, description: str | None = None) -> GraphQLObjectType:
    """
    Create a new GraphQL object type.

    Args:
        name: Type name
        description: Type description

    Returns:
        GraphQLObjectType instance
    """
    return GraphQLObjectType(name=name, description=description)

def create_field(name: str, type: str | GraphQLObjectType,
                description: str | None = None, required: bool = False) -> GraphQLField:
    """
    Create a new GraphQL field.

    Args:
        name: Field name
        type: Field type
        description: Field description
        required: Whether the field is required

    Returns:
        GraphQLField instance
    """
    return GraphQLField(
        name=name,
        type=type,
        description=description,
        required=required
    )
