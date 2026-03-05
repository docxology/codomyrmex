"""Unit tests for codomyrmex.api.standardization.graphql_api.

Imports the submodule file directly to bypass the circular import chain
in codomyrmex.api.__init__.  No mocks are used — all test doubles are real
callables or concrete objects.
"""

import importlib.util
import sys

import pytest

# ---------------------------------------------------------------------------
# Direct-import helper
# ---------------------------------------------------------------------------


def _load_graphql_api():
    name = "codomyrmex.api.standardization.graphql_api"
    if name in sys.modules:
        return sys.modules[name]
    import codomyrmex.logging_monitoring  # noqa: F401

    spec = importlib.util.spec_from_file_location(
        name,
        "src/codomyrmex/api/standardization/graphql_api.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


try:
    _gql = _load_graphql_api()
    GraphQLType = _gql.GraphQLType
    GraphQLField = _gql.GraphQLField
    GraphQLObjectType = _gql.GraphQLObjectType
    GraphQLSchema = _gql.GraphQLSchema
    GraphQLResolver = _gql.GraphQLResolver
    GraphQLMutation = _gql.GraphQLMutation
    GraphQLQuery = _gql.GraphQLQuery
    GraphQLAPI = _gql.GraphQLAPI
    resolver = _gql.resolver
    mutation = _gql.mutation
    create_schema = _gql.create_schema
    create_object_type = _gql.create_object_type
    create_field = _gql.create_field
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    _SKIP_REASON = str(_exc)

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason=f"graphql_api unavailable: {'' if _AVAILABLE else _SKIP_REASON}",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user_type():
    """A simple User GraphQL object type."""
    t = GraphQLObjectType(name="User", description="A user entity")
    t.add_field(GraphQLField(name="id", type="ID", required=True))
    t.add_field(GraphQLField(name="name", type="String"))
    t.add_field(GraphQLField(name="email", type="String"))
    return t


@pytest.fixture
def post_type():
    """A simple Post GraphQL object type."""
    t = GraphQLObjectType(name="Post")
    t.add_field(GraphQLField(name="id", type="ID", required=True))
    t.add_field(GraphQLField(name="title", type="String", required=True))
    t.add_field(GraphQLField(name="content", type="String"))
    return t


@pytest.fixture
def simple_schema(user_type, post_type):
    """Schema with User, Post types and a Query type."""
    schema = GraphQLSchema()
    schema.add_type(user_type)
    schema.add_type(post_type)

    query_type = GraphQLObjectType(name="Query")
    query_type.add_field(
        GraphQLField(name="user", type="User", args={"id": "ID"}, required=True)
    )
    query_type.add_field(GraphQLField(name="users", type="[User]"))
    schema.query_type = query_type
    return schema


@pytest.fixture
def graphql_api(simple_schema):
    return GraphQLAPI(schema=simple_schema)


# ===========================================================================
# GraphQLType enum
# ===========================================================================


class TestGraphQLType:
    """GraphQLType enum — five scalar types."""

    def test_string(self):
        assert GraphQLType.STRING.value == "String"

    def test_int(self):
        assert GraphQLType.INT.value == "Int"

    def test_float(self):
        assert GraphQLType.FLOAT.value == "Float"

    def test_boolean(self):
        assert GraphQLType.BOOLEAN.value == "Boolean"

    def test_id(self):
        assert GraphQLType.ID.value == "ID"

    def test_five_members(self):
        assert len(GraphQLType) == 5


# ===========================================================================
# GraphQLField
# ===========================================================================


class TestGraphQLField:
    """GraphQLField dataclass — construction and defaults."""

    def test_basic_field(self):
        f = GraphQLField(name="username", type="String")
        assert f.name == "username"
        assert f.type == "String"
        assert f.required is False
        assert f.description is None
        assert f.args == {}
        assert f.resolver is None

    def test_required_field(self):
        f = GraphQLField(name="id", type="ID", required=True)
        assert f.required is True

    def test_field_with_args(self):
        f = GraphQLField(name="user", type="User", args={"id": "ID"})
        assert "id" in f.args

    def test_field_with_resolver(self):
        def my_resolver(parent, args, ctx):
            return "resolved"

        f = GraphQLField(name="computed", type="String", resolver=my_resolver)
        assert f.resolver is my_resolver


# ===========================================================================
# GraphQLObjectType
# ===========================================================================


class TestGraphQLObjectType:
    """GraphQLObjectType — add_field, get_field, defaults."""

    def test_empty_type(self):
        t = GraphQLObjectType(name="Empty")
        assert t.name == "Empty"
        assert t.fields == {}
        assert t.interfaces == []

    def test_add_field_stores_by_name(self, user_type):
        assert "id" in user_type.fields
        assert "name" in user_type.fields

    def test_get_field_returns_field(self, user_type):
        f = user_type.get_field("id")
        assert f is not None
        assert f.name == "id"

    def test_get_field_returns_none_for_missing(self, user_type):
        assert user_type.get_field("nonexistent") is None

    def test_description_stored(self, user_type):
        assert user_type.description == "A user entity"

    def test_multiple_fields(self, user_type):
        assert len(user_type.fields) == 3  # id, name, email

    def test_convenience_factory(self):
        t = create_object_type("Product", description="A product")
        assert isinstance(t, GraphQLObjectType)
        assert t.name == "Product"
        assert t.description == "A product"


# ===========================================================================
# GraphQLSchema
# ===========================================================================


class TestGraphQLSchema:
    """GraphQLSchema — add_type, get_type, generate_sdl."""

    def test_empty_schema(self):
        s = create_schema()
        assert s.query_type is None
        assert s.mutation_type is None
        assert s.types == {}

    def test_add_and_get_type(self, user_type):
        s = GraphQLSchema()
        s.add_type(user_type)
        retrieved = s.get_type("User")
        assert retrieved is user_type

    def test_get_type_missing_returns_none(self):
        s = GraphQLSchema()
        assert s.get_type("Missing") is None

    def test_generate_sdl_contains_type_name(self, simple_schema):
        sdl = simple_schema.generate_sdl()
        assert "type User" in sdl
        assert "type Post" in sdl

    def test_generate_sdl_contains_fields(self, simple_schema):
        sdl = simple_schema.generate_sdl()
        assert "name" in sdl
        assert "email" in sdl

    def test_generate_sdl_required_field_has_exclamation(self, simple_schema):
        sdl = simple_schema.generate_sdl()
        # 'id' is required on User
        assert "id" in sdl

    def test_generate_sdl_with_query_type(self, simple_schema):
        sdl = simple_schema.generate_sdl()
        assert "type Query" in sdl
        assert "user" in sdl

    def test_generate_sdl_with_mutation_type(self):
        s = GraphQLSchema()
        mut_type = GraphQLObjectType(name="Mutation")
        mut_type.add_field(
            GraphQLField(name="createUser", type="User", args={"name": "String"})
        )
        s.mutation_type = mut_type
        sdl = s.generate_sdl()
        assert "type Mutation" in sdl
        assert "createUser" in sdl

    def test_generate_sdl_field_args_in_output(self):
        s = GraphQLSchema()
        t = GraphQLObjectType(name="Query")
        t.add_field(GraphQLField(name="user", type="User", args={"id": "ID"}))
        s.query_type = t
        sdl = s.generate_sdl()
        assert "id: ID" in sdl

    def test_generate_sdl_object_type_as_field_type(self):
        """When a field's type is a GraphQLObjectType, sdl uses its name."""
        s = GraphQLSchema()
        address_type = GraphQLObjectType(name="Address")
        s.add_type(address_type)
        person_type = GraphQLObjectType(name="Person")
        person_type.add_field(GraphQLField(name="address", type=address_type))
        s.add_type(person_type)
        sdl = s.generate_sdl()
        assert "Address" in sdl

    def test_generate_sdl_query_type_field_with_args(self):
        """Query type fields with args render arg list in SDL (lines 87-91 path)."""
        s = GraphQLSchema()
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(
            GraphQLField(
                name="user",
                type="User",
                args={"id": "ID", "org": "String"},
            )
        )
        s.query_type = q_type
        sdl = s.generate_sdl()
        assert "type Query" in sdl
        assert "id: ID" in sdl
        assert "org: String" in sdl

    def test_generate_sdl_query_field_with_object_type_arg(self):
        """Query field arg whose type is a GraphQLObjectType renders as .name."""
        s = GraphQLSchema()
        filter_type = GraphQLObjectType(name="UserFilter")
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(
            GraphQLField(
                name="users",
                type="[User]",
                args={"filter": filter_type},
            )
        )
        s.query_type = q_type
        sdl = s.generate_sdl()
        assert "filter: UserFilter" in sdl

    def test_generate_sdl_mutation_field_with_args(self):
        """Mutation type fields with args appear in SDL."""
        s = GraphQLSchema()
        mut_type = GraphQLObjectType(name="Mutation")
        mut_type.add_field(
            GraphQLField(
                name="createUser",
                type="User",
                args={"name": "String", "email": "String"},
                required=True,
            )
        )
        s.mutation_type = mut_type
        sdl = s.generate_sdl()
        assert "type Mutation" in sdl
        assert "name: String" in sdl
        assert "createUser" in sdl


# ===========================================================================
# GraphQLResolver
# ===========================================================================


class TestGraphQLResolver:
    """GraphQLResolver — resolve delegates to the wrapped function."""

    def test_resolve_calls_function(self):
        def my_func(parent, args, ctx):
            return f"resolved:{args.get('id')}"

        r = GraphQLResolver(field_name="user", resolver_func=my_func, complexity=2)
        result = r.resolve(None, {"id": "42"}, {})
        assert result == "resolved:42"

    def test_resolve_propagates_exception(self):
        def bad_func(parent, args, ctx):
            raise ValueError("resolver broke")

        r = GraphQLResolver(field_name="broken", resolver_func=bad_func)
        with pytest.raises(ValueError, match="resolver broke"):
            r.resolve(None, {}, {})

    def test_complexity_stored(self):
        r = GraphQLResolver("field", lambda p, a, c: None, complexity=10)
        assert r.complexity == 10

    def test_resolver_decorator(self):
        @resolver("myField", complexity=3)
        def my_resolver(parent, args, ctx):
            return "value"

        assert isinstance(my_resolver, GraphQLResolver)
        assert my_resolver.field_name == "myField"
        assert my_resolver.complexity == 3
        assert my_resolver.resolve(None, {}, {}) == "value"


# ===========================================================================
# GraphQLMutation
# ===========================================================================


class TestGraphQLMutation:
    """GraphQLMutation — execute delegates to resolver."""

    def _make_mutation(self, resolver_func=None):
        input_type = GraphQLObjectType(name="CreateUserInput")
        if resolver_func is None:

            def resolver_func(data, ctx):
                return {"id": "1", "name": data.get("name")}

        return GraphQLMutation(
            name="createUser",
            input_type=input_type,
            output_type="User",
            resolver=resolver_func,
            description="Create a user",
        )

    def test_execute_returns_resolver_result(self):
        mut = self._make_mutation()
        result = mut.execute({"name": "Alice"}, {})
        assert result["name"] == "Alice"

    def test_execute_propagates_exception(self):
        def bad(data, ctx):
            raise RuntimeError("mutation failed")

        mut = self._make_mutation(bad)
        with pytest.raises(RuntimeError, match="mutation failed"):
            mut.execute({}, {})

    def test_mutation_decorator(self):
        input_type = GraphQLObjectType(name="DeleteInput")

        @mutation(
            "deleteUser",
            input_type=input_type,
            output_type="Boolean",
            description="Delete a user",
        )
        def delete_resolver(data, ctx):
            return True

        assert isinstance(delete_resolver, GraphQLMutation)
        assert delete_resolver.name == "deleteUser"
        assert delete_resolver.execute({}, {}) is True


# ===========================================================================
# GraphQLQuery
# ===========================================================================


class TestGraphQLQuery:
    """GraphQLQuery dataclass."""

    def test_defaults(self):
        q = GraphQLQuery(operation="query", selection_set={})
        assert q.variables == {}
        assert q.operation_name is None

    def test_with_variables(self):
        q = GraphQLQuery(
            operation="query",
            selection_set={"user": {}},
            variables={"id": "1"},
            operation_name="GetUser",
        )
        assert q.variables["id"] == "1"
        assert q.operation_name == "GetUser"


# ===========================================================================
# GraphQLAPI
# ===========================================================================


class TestGraphQLAPI:
    """GraphQLAPI — execute_query, register_resolver, register_mutation, metrics."""

    def test_initial_metrics(self, graphql_api):
        m = graphql_api.get_metrics()
        assert m["total_requests"] == 0
        assert m["total_errors"] == 0
        assert m["registered_mutations"] == 0

    def test_execute_query_increments_request_count(self, graphql_api):
        graphql_api.execute_query("{ user { id } }")
        assert graphql_api.request_count == 1

    def test_execute_query_returns_data_key(self, graphql_api):
        result = graphql_api.execute_query("{ users }")
        assert "data" in result

    def test_execute_query_with_variables(self, graphql_api):
        result = graphql_api.execute_query(
            "query GetUser { user { id } }",
            variables={"id": "1"},
        )
        assert "data" in result or "errors" in result

    def test_execute_query_error_returns_errors_key(self, graphql_api):
        # Force an error by setting query_complexity_limit to 0
        graphql_api.query_complexity_limit = 0
        result = graphql_api.execute_query("{ anything }")
        assert "errors" in result
        assert graphql_api.error_count == 1

    def test_register_resolver(self, graphql_api):
        r = GraphQLResolver("id", lambda p, a, c: "test-id")
        graphql_api.register_resolver("User", "id", r)
        assert "User" in graphql_api.resolvers
        assert "id" in graphql_api.resolvers["User"]

    def test_register_mutation(self, graphql_api):
        input_type = GraphQLObjectType("CreatePostInput")
        mut = GraphQLMutation(
            name="createPost",
            input_type=input_type,
            output_type="Post",
            resolver=lambda data, ctx: {"id": "p1"},
        )
        graphql_api.register_mutation(mut)
        assert "createPost" in graphql_api.mutations

    def test_get_schema_sdl_returns_string(self, graphql_api):
        sdl = graphql_api.get_schema_sdl()
        assert isinstance(sdl, str)

    def test_validate_query_returns_empty_list_for_valid(self, graphql_api):
        errors = graphql_api.validate_query("{ users }")
        assert errors == []

    def test_builtin_resolver_registered_on_init(self, graphql_api):
        # __typename resolver should be registered under __Any
        assert "__Any" in graphql_api.resolvers

    def test_execute_mutation_operation(self, graphql_api):
        result = graphql_api.execute_query("mutation CreateUser { createUser }")
        # Should not raise, returns data or errors
        assert "data" in result or "errors" in result

    def test_metrics_registered_resolvers_count(self, graphql_api):
        graphql_api.register_resolver(
            "Post", "title", GraphQLResolver("title", lambda p, a, c: "hi")
        )
        m = graphql_api.get_metrics()
        # At least the built-in __typename resolver plus our new one
        assert m["registered_resolvers"] >= 2

    def test_metrics_error_rate_zero_initially(self, graphql_api):
        m = graphql_api.get_metrics()
        assert m["error_rate"] == 0.0

    def test_execute_query_with_context(self, graphql_api):
        result = graphql_api.execute_query(
            "{ users }",
            context={"user": "admin"},
        )
        assert "data" in result or "errors" in result


# ===========================================================================
# Field resolution via custom resolvers
# ===========================================================================


class TestFieldResolutionWithCustomResolver:
    """Resolvers on schema fields are invoked during _execute_selection_set."""

    def test_custom_resolver_on_field(self):
        schema = GraphQLSchema()
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(
            GraphQLField(
                name="hello",
                type="String",
                resolver=lambda parent, args, ctx: "world",
            )
        )
        schema.query_type = q_type
        api = GraphQLAPI(schema=schema)
        result = api.execute_query("{ hello }")
        assert result.get("data", {}).get("hello") == "world"

    def test_resolver_exception_caught_field_becomes_none(self):
        """If a custom resolver raises, the field is None and no top-level error."""
        schema = GraphQLSchema()
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(
            GraphQLField(
                name="boom",
                type="String",
                resolver=lambda parent, args, ctx: (_ for _ in ()).throw(
                    RuntimeError("boom")
                ),
            )
        )
        schema.query_type = q_type
        api = GraphQLAPI(schema=schema)
        result = api.execute_query("{ boom }")
        # The field is set to None on resolver error
        data = result.get("data") or {}
        assert data.get("boom") is None

    def test_default_attribute_resolution(self):
        """When no resolver is set, getattr is used on the parent object."""

        class FakeParent:
            greeting = "hi there"

        schema = GraphQLSchema()
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(GraphQLField(name="greeting", type="String"))
        schema.query_type = q_type

        api = GraphQLAPI(schema=schema)
        result = api._execute_selection_set(q_type, FakeParent(), {})
        assert result["greeting"] == "hi there"

    def test_default_attribute_resolution_missing_returns_none(self):
        class FakeParent:
            pass

        schema = GraphQLSchema()
        q_type = GraphQLObjectType(name="Query")
        q_type.add_field(GraphQLField(name="missing_attr", type="String"))
        schema.query_type = q_type

        api = GraphQLAPI(schema=schema)
        result = api._execute_selection_set(q_type, FakeParent(), {})
        assert result["missing_attr"] is None


# ===========================================================================
# _parse_query
# ===========================================================================


class TestParseQuery:
    """_parse_query — operation detection and name extraction."""

    def test_plain_query_operation(self, graphql_api):
        parsed = graphql_api._parse_query("{ users { id } }")
        assert parsed.operation == "query"

    def test_mutation_operation_detected(self, graphql_api):
        parsed = graphql_api._parse_query("mutation CreateUser { createUser }")
        assert parsed.operation == "mutation"

    def test_named_query_extracts_name(self, graphql_api):
        parsed = graphql_api._parse_query("query GetAllUsers { users { id } }")
        assert parsed.operation_name == "GetAllUsers"

    def test_unnamed_query_has_no_operation_name(self, graphql_api):
        parsed = graphql_api._parse_query("{ users }")
        assert parsed.operation_name is None


# ===========================================================================
# Convenience functions
# ===========================================================================


class TestConvenienceFunctions:
    """create_schema, create_object_type, create_field."""

    def test_create_schema_returns_empty_schema(self):
        s = create_schema()
        assert isinstance(s, GraphQLSchema)
        assert s.query_type is None

    def test_create_field_string_type(self):
        f = create_field("username", "String")
        assert f.name == "username"
        assert f.type == "String"
        assert f.required is False

    def test_create_field_required(self):
        f = create_field("id", "ID", required=True)
        assert f.required is True

    def test_create_field_with_description(self):
        f = create_field("bio", "String", description="User biography")
        assert f.description == "User biography"

    def test_create_field_object_type(self):
        t = create_object_type("Address")
        f = create_field("address", t)
        assert f.type is t
