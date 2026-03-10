"""
Comprehensive unit tests for InfomaniakHeatClient (orchestration).

Tests cover all methods:
- Stack CRUD: list, get, create, create_from_file, update, delete, suspend, resume
- Resources: list_stack_resources, get_stack_resource
- Events: list_stack_events (with and without resource_name filter)
- Templates: validate_template (success/failure), get_stack_template
- Outputs: get_stack_outputs (with outputs, empty, stack not found)
- Error handling: every method gracefully handles exceptions

Uses stub_openstack_connection fixture and make_stub_stack factory from conftest.py.

Total: ~26 tests in TestInfomaniakOrchestration class.
"""

from _stubs import Stub, make_stub_stack

from codomyrmex.cloud.infomaniak.orchestration.client import InfomaniakHeatClient


class TestInfomaniakOrchestration:
    """Comprehensive tests for InfomaniakHeatClient."""

    # =====================================================================
    # Stack Operations
    # =====================================================================

    def test_list_stacks_success(self, stub_openstack_connection):
        """list_stacks returns formatted dicts for each stack."""
        stack = make_stub_stack(
            stack_id="stk-1", name="web-app", status="CREATE_COMPLETE"
        )
        stub_openstack_connection.orchestration.stacks.return_value = [stack]

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stacks()

        assert len(result) == 1
        assert result[0]["id"] == "stk-1"
        assert result[0]["name"] == "web-app"
        assert result[0]["status"] == "CREATE_COMPLETE"
        assert result[0]["status_reason"] == "Stack CREATE_COMPLETE"
        assert result[0]["creation_time"] is None

    def test_list_stacks_error_returns_empty(self, stub_openstack_connection):
        """list_stacks returns empty list on connection error."""
        stub_openstack_connection.orchestration.stacks.side_effect = Exception(
            "Timeout"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stacks()

        assert result == []

    def test_get_stack_success(self, stub_openstack_connection):
        """get_stack returns full stack detail dict when found."""
        stack = make_stub_stack(stack_id="stk-abc", name="db-stack")
        stub_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack("stk-abc")

        assert result is not None
        assert result["id"] == "stk-abc"
        assert result["name"] == "db-stack"
        assert result["description"] == "Test stack"
        assert result["parameters"] == {"key": "value"}
        assert len(result["outputs"]) == 1
        assert result["outputs"][0]["output_key"] == "ip"
        stub_openstack_connection.orchestration.find_stack.assert_called_once_with(
            "stk-abc"
        )

    def test_get_stack_not_found(self, stub_openstack_connection):
        """get_stack returns None when find_stack returns None."""
        stub_openstack_connection.orchestration.find_stack.return_value = None

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack("nonexistent")

        assert result is None

    def test_get_stack_error_returns_none(self, stub_openstack_connection):
        """get_stack returns None on exception."""
        stub_openstack_connection.orchestration.find_stack.side_effect = Exception(
            "Auth fail"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack("stk-err")

        assert result is None

    def test_create_stack_success(self, stub_openstack_connection):
        """create_stack returns dict with id and name on success."""
        stub_stack_result = Stub()
        stub_stack_result.id = "stk-new"
        stub_openstack_connection.orchestration.create_stack.return_value = (
            stub_stack_result
        )

        template = "heat_template_version: 2021-04-16\nresources: {}"

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.create_stack(
            name="fresh-stack",
            template=template,
            parameters={"image": "Ubuntu 22.04"},
            environment={"param_defaults": {}},
            timeout_mins=45,
            disable_rollback=True,
        )

        assert result is not None
        assert result["id"] == "stk-new"
        assert result["name"] == "fresh-stack"
        stub_openstack_connection.orchestration.create_stack.assert_called_once_with(
            name="fresh-stack",
            template=template,
            parameters={"image": "Ubuntu 22.04"},
            environment={"param_defaults": {}},
            timeout_mins=45,
            disable_rollback=True,
        )

    def test_create_stack_error_returns_none(self, stub_openstack_connection):
        """create_stack returns None on exception."""
        stub_openstack_connection.orchestration.create_stack.side_effect = Exception(
            "Quota exceeded"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.create_stack(name="fail-stack", template="bad")

        assert result is None

    def test_create_stack_from_file_success(self, stub_openstack_connection, tmp_path):
        """create_stack_from_file reads file and delegates to create_stack."""
        stub_stack_result = Stub()
        stub_stack_result.id = "stk-from-file"
        stub_openstack_connection.orchestration.create_stack.return_value = (
            stub_stack_result
        )

        template_content = "heat_template_version: 2021-04-16\nresources:\n  server:\n    type: OS::Nova::Server"
        template_file = tmp_path / "template.yaml"
        template_file.write_text(template_content)

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.create_stack_from_file(
            name="file-stack",
            template_path=str(template_file),
            parameters={"key_name": "ssh-key"},
        )

        assert result is not None
        assert result["id"] == "stk-from-file"
        stub_openstack_connection.orchestration.create_stack.assert_called_once()

    def test_create_stack_from_file_read_error(self, stub_openstack_connection):
        """create_stack_from_file returns None when file cannot be read."""
        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.create_stack_from_file(
            name="missing-file-stack",
            template_path="/nonexistent_path_xyz123/template.yaml",
        )

        assert result is None

    def test_update_stack_success(self, stub_openstack_connection):
        """update_stack returns True on successful update."""
        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.update_stack(
            stack_id="stk-upd",
            template="heat_template_version: 2021-04-16",
            parameters={"image": "Ubuntu 24.04"},
            environment={"resource_registry": {}},
        )

        assert result is True
        stub_openstack_connection.orchestration.update_stack.assert_called_once_with(
            "stk-upd",
            template="heat_template_version: 2021-04-16",
            parameters={"image": "Ubuntu 24.04"},
            environment={"resource_registry": {}},
        )

    def test_update_stack_error_returns_false(self, stub_openstack_connection):
        """update_stack returns False on exception."""
        stub_openstack_connection.orchestration.update_stack.side_effect = Exception(
            "Stack in DELETE_IN_PROGRESS"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.update_stack("stk-bad", template="new-template")

        assert result is False

    def test_delete_stack_success(self, stub_openstack_connection):
        """delete_stack returns True on successful deletion."""
        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.delete_stack("stk-del")

        assert result is True
        stub_openstack_connection.orchestration.delete_stack.assert_called_once_with(
            "stk-del"
        )

    def test_delete_stack_error_returns_false(self, stub_openstack_connection):
        """delete_stack returns False on exception."""
        stub_openstack_connection.orchestration.delete_stack.side_effect = Exception(
            "Not found"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.delete_stack("stk-gone")

        assert result is False

    def test_suspend_stack_success(self, stub_openstack_connection):
        """suspend_stack returns True on success."""
        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.suspend_stack("stk-suspend")

        assert result is True
        stub_openstack_connection.orchestration.suspend_stack.assert_called_once_with(
            "stk-suspend"
        )

    def test_suspend_stack_error_returns_false(self, stub_openstack_connection):
        """suspend_stack returns False on exception."""
        stub_openstack_connection.orchestration.suspend_stack.side_effect = Exception(
            "Already suspended"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.suspend_stack("stk-already-sus")

        assert result is False

    def test_resume_stack_success(self, stub_openstack_connection):
        """resume_stack returns True on success."""
        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.resume_stack("stk-resume")

        assert result is True
        stub_openstack_connection.orchestration.resume_stack.assert_called_once_with(
            "stk-resume"
        )

    def test_resume_stack_error_returns_false(self, stub_openstack_connection):
        """resume_stack returns False on exception."""
        stub_openstack_connection.orchestration.resume_stack.side_effect = Exception(
            "Not suspended"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.resume_stack("stk-not-sus")

        assert result is False

    # =====================================================================
    # Stack Resources
    # =====================================================================

    def test_list_stack_resources_success(self, stub_openstack_connection):
        """list_stack_resources returns formatted resource dicts."""
        stub_resource = Stub()
        stub_resource.name = "my_server"
        stub_resource.resource_type = "OS::Nova::Server"
        stub_resource.status = "CREATE_COMPLETE"
        stub_resource.status_reason = "state changed"
        stub_resource.physical_resource_id = "srv-phys-001"

        stub_openstack_connection.orchestration.resources.return_value = [stub_resource]

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stack_resources("stk-res")

        assert len(result) == 1
        assert result[0]["name"] == "my_server"
        assert result[0]["resource_type"] == "OS::Nova::Server"
        assert result[0]["status"] == "CREATE_COMPLETE"
        assert result[0]["physical_resource_id"] == "srv-phys-001"
        stub_openstack_connection.orchestration.resources.assert_called_once_with(
            "stk-res"
        )

    def test_list_stack_resources_error_returns_empty(self, stub_openstack_connection):
        """list_stack_resources returns empty list on exception."""
        stub_openstack_connection.orchestration.resources.side_effect = Exception(
            "Not found"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stack_resources("stk-bad")

        assert result == []

    def test_get_stack_resource_success(self, stub_openstack_connection):
        """get_stack_resource returns formatted dict for a single resource."""
        stub_resource = Stub()
        stub_resource.name = "my_network"
        stub_resource.resource_type = "OS::Neutron::Net"
        stub_resource.status = "CREATE_COMPLETE"
        stub_resource.physical_resource_id = "net-phys-002"
        stub_resource.attributes = {"admin_state_up": True}

        stub_openstack_connection.orchestration.get_resource.return_value = (
            stub_resource
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_resource("stk-123", "my_network")

        assert result is not None
        assert result["name"] == "my_network"
        assert result["resource_type"] == "OS::Neutron::Net"
        assert result["attributes"]["admin_state_up"] is True
        stub_openstack_connection.orchestration.get_resource.assert_called_once_with(
            "stk-123", "my_network"
        )

    def test_get_stack_resource_error_returns_none(self, stub_openstack_connection):
        """get_stack_resource returns None on exception."""
        stub_openstack_connection.orchestration.get_resource.side_effect = Exception(
            "Resource not found"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_resource("stk-123", "nonexistent")

        assert result is None

    # =====================================================================
    # Stack Events
    # =====================================================================

    def test_list_stack_events_success(self, stub_openstack_connection):
        """list_stack_events returns formatted event dicts."""
        stub_event = Stub()
        stub_event.id = "evt-001"
        stub_event.resource_name = "my_server"
        stub_event.resource_status = "CREATE_COMPLETE"
        stub_event.resource_status_reason = "state changed"
        stub_event.event_time = "2026-01-15T10:30:00Z"

        stub_openstack_connection.orchestration.events.return_value = [stub_event]

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stack_events("stk-evt")

        assert len(result) == 1
        assert result[0]["id"] == "evt-001"
        assert result[0]["resource_name"] == "my_server"
        assert result[0]["resource_status"] == "CREATE_COMPLETE"
        assert result[0]["event_time"] == "2026-01-15T10:30:00Z"
        stub_openstack_connection.orchestration.events.assert_called_once_with(
            "stk-evt", None
        )

    def test_list_stack_events_with_resource_filter(self, stub_openstack_connection):
        """list_stack_events passes resource_name filter to SDK."""
        stub_openstack_connection.orchestration.events.return_value = []

        client = InfomaniakHeatClient(stub_openstack_connection)
        client.list_stack_events("stk-evt", resource_name="my_server")

        stub_openstack_connection.orchestration.events.assert_called_once_with(
            "stk-evt", "my_server"
        )

    def test_list_stack_events_error_returns_empty(self, stub_openstack_connection):
        """list_stack_events returns empty list on exception."""
        stub_openstack_connection.orchestration.events.side_effect = Exception(
            "Stack gone"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.list_stack_events("stk-gone")

        assert result == []

    # =====================================================================
    # Template Operations
    # =====================================================================

    def test_validate_template_success(self, stub_openstack_connection):
        """validate_template returns valid=True with description and parameters."""
        stub_openstack_connection.orchestration.validate_template.return_value = {
            "Description": "Web application stack",
            "Parameters": {
                "image": {"Type": "String", "Default": "Ubuntu 22.04"},
                "flavor": {"Type": "String", "Default": "a1-ram2-disk20-perf1"},
            },
        }

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.validate_template(
            template="heat_template_version: 2021-04-16",
            environment={"resource_registry": {}},
        )

        assert result["valid"] is True
        assert result["description"] == "Web application stack"
        assert "image" in result["parameters"]
        assert "flavor" in result["parameters"]
        stub_openstack_connection.orchestration.validate_template.assert_called_once_with(
            template="heat_template_version: 2021-04-16",
            environment={"resource_registry": {}},
        )

    def test_validate_template_failure(self, stub_openstack_connection):
        """validate_template returns valid=False with error on invalid template."""
        stub_openstack_connection.orchestration.validate_template.side_effect = (
            Exception("Invalid template: missing heat_template_version")
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.validate_template(template="not: valid: yaml: garbage")

        assert result["valid"] is False
        assert "Invalid template" in result["error"]
        assert "heat_template_version" in result["error"]

    def test_get_stack_template_success(self, stub_openstack_connection):
        """get_stack_template returns template string on success."""
        expected_template = "heat_template_version: 2021-04-16\nresources:\n  server:\n    type: OS::Nova::Server"
        stub_openstack_connection.orchestration.get_stack_template.return_value = (
            expected_template
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_template("stk-tmpl")

        assert result == expected_template
        stub_openstack_connection.orchestration.get_stack_template.assert_called_once_with(
            "stk-tmpl"
        )

    def test_get_stack_template_error_returns_none(self, stub_openstack_connection):
        """get_stack_template returns None on exception."""
        stub_openstack_connection.orchestration.get_stack_template.side_effect = (
            Exception("Stack not found")
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_template("stk-missing")

        assert result is None

    # =====================================================================
    # Stack Outputs
    # =====================================================================

    def test_get_stack_outputs_with_outputs(self, stub_openstack_connection):
        """get_stack_outputs returns key-value dict from stack outputs."""
        stack = make_stub_stack(stack_id="stk-out")
        stack.outputs = [
            {"output_key": "public_ip", "output_value": "195.15.220.10"},
            {"output_key": "private_ip", "output_value": "10.0.0.5"},
            {"output_key": "url", "output_value": "https://app.example.com"},
        ]
        stub_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_outputs("stk-out")

        assert result["public_ip"] == "195.15.220.10"
        assert result["private_ip"] == "10.0.0.5"
        assert result["url"] == "https://app.example.com"
        assert len(result) == 3

    def test_get_stack_outputs_empty(self, stub_openstack_connection):
        """get_stack_outputs returns empty dict when stack has no outputs."""
        stack = make_stub_stack(stack_id="stk-no-out")
        stack.outputs = []
        stub_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_outputs("stk-no-out")

        assert result == {}

    def test_get_stack_outputs_stack_not_found(self, stub_openstack_connection):
        """get_stack_outputs returns empty dict when stack does not exist."""
        stub_openstack_connection.orchestration.find_stack.return_value = None

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_outputs("stk-gone")

        assert result == {}

    def test_get_stack_outputs_error_returns_empty(self, stub_openstack_connection):
        """get_stack_outputs returns empty dict on exception."""
        stub_openstack_connection.orchestration.find_stack.side_effect = Exception(
            "Network error"
        )

        client = InfomaniakHeatClient(stub_openstack_connection)
        result = client.get_stack_outputs("stk-err")

        assert result == {}


# =========================================================================


class TestInfomaniakHeatClientExpanded:
    """Tests for InfomaniakHeatClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        stub_conn = Stub()
        return InfomaniakHeatClient(connection=stub_conn), stub_conn

    def test_update_stack(self):
        client, mc = self._make_client()
        assert client.update_stack("stk1", template="heat: {}") is True
        mc.orchestration.update_stack.assert_called_once()

    def test_suspend_stack(self):
        client, mc = self._make_client()
        assert client.suspend_stack("stk1") is True
        mc.orchestration.suspend_stack.assert_called_once_with("stk1")

    def test_resume_stack(self):
        client, mc = self._make_client()
        assert client.resume_stack("stk1") is True
        mc.orchestration.resume_stack.assert_called_once_with("stk1")

    def test_get_stack_resource(self):
        client, mc = self._make_client()
        res = Stub(
            name="srv",
            resource_type="OS::Nova::Server",
            status="CREATE_COMPLETE",
            physical_resource_id="inst1",
            attributes={"ip": "1.2.3.4"},
        )
        mc.orchestration.get_resource.return_value = res
        result = client.get_stack_resource("stk1", "srv")
        assert result["resource_type"] == "OS::Nova::Server"

    def test_list_stack_events(self):
        client, mc = self._make_client()
        ev = Stub(
            id="ev1",
            resource_name="srv",
            resource_status="CREATE_COMPLETE",
            resource_status_reason="OK",
            event_time=None,
        )
        mc.orchestration.events.return_value = [ev]
        result = client.list_stack_events("stk1")
        assert len(result) == 1
        assert result[0]["resource_name"] == "srv"

    def test_get_stack_template(self):
        client, mc = self._make_client()
        tpl = "heat_template_version: 2021-04-16"
        mc.orchestration.get_stack_template.return_value = tpl
        assert client.get_stack_template("stk1") == tpl

    def test_get_stack_outputs(self):
        client, mc = self._make_client()
        stk = Stub()
        stk.outputs = [{"output_key": "server_ip", "output_value": "10.0.0.5"}]
        mc.orchestration.find_stack.return_value = stk
        result = client.get_stack_outputs("stk1")
        assert result["server_ip"] == "10.0.0.5"

    def test_list_stacks_error(self):
        client, mc = self._make_client()
        mc.orchestration.stacks.side_effect = Exception("fail")
        assert client.list_stacks() == []


# =========================================================================
# ADDITIONAL METERING CLIENT TESTS
# =========================================================================
