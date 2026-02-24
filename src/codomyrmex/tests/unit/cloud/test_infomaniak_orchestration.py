"""
Comprehensive unit tests for InfomaniakHeatClient (orchestration).

Tests cover all methods:
- Stack CRUD: list, get, create, create_from_file, update, delete, suspend, resume
- Resources: list_stack_resources, get_stack_resource
- Events: list_stack_events (with and without resource_name filter)
- Templates: validate_template (success/failure), get_stack_template
- Outputs: get_stack_outputs (with outputs, empty, stack not found)
- Error handling: every method gracefully handles exceptions

Uses mock_openstack_connection fixture and make_stub_stack factory from conftest.py.

Total: ~26 tests in TestInfomaniakOrchestration class.
"""

import os
from _stubs import Stub


from codomyrmex.cloud.infomaniak.orchestration.client import InfomaniakHeatClient

from _stubs import make_stub_stack


class TestInfomaniakOrchestration:
    """Comprehensive tests for InfomaniakHeatClient."""

    # =====================================================================
    # Stack Operations
    # =====================================================================

    def test_list_stacks_success(self, mock_openstack_connection):
        """list_stacks returns formatted dicts for each stack."""
        stack = make_stub_stack(stack_id="stk-1", name="web-app", status="CREATE_COMPLETE")
        mock_openstack_connection.orchestration.stacks.return_value = [stack]

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stacks()

        assert len(result) == 1
        assert result[0]["id"] == "stk-1"
        assert result[0]["name"] == "web-app"
        assert result[0]["status"] == "CREATE_COMPLETE"
        assert result[0]["status_reason"] == "Stack CREATE_COMPLETE"
        assert result[0]["creation_time"] is None

    def test_list_stacks_error_returns_empty(self, mock_openstack_connection):
        """list_stacks returns empty list on connection error."""
        mock_openstack_connection.orchestration.stacks.side_effect = Exception("Timeout")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stacks()

        assert result == []

    def test_get_stack_success(self, mock_openstack_connection):
        """get_stack returns full stack detail dict when found."""
        stack = make_stub_stack(stack_id="stk-abc", name="db-stack")
        mock_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack("stk-abc")

        assert result is not None
        assert result["id"] == "stk-abc"
        assert result["name"] == "db-stack"
        assert result["description"] == "Test stack"
        assert result["parameters"] == {"key": "value"}
        assert len(result["outputs"]) == 1
        assert result["outputs"][0]["output_key"] == "ip"
        mock_openstack_connection.orchestration.find_stack.assert_called_once_with("stk-abc")

    def test_get_stack_not_found(self, mock_openstack_connection):
        """get_stack returns None when find_stack returns None."""
        mock_openstack_connection.orchestration.find_stack.return_value = None

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack("nonexistent")

        assert result is None

    def test_get_stack_error_returns_none(self, mock_openstack_connection):
        """get_stack returns None on exception."""
        mock_openstack_connection.orchestration.find_stack.side_effect = Exception("Auth fail")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack("stk-err")

        assert result is None

    def test_create_stack_success(self, mock_openstack_connection):
        """create_stack returns dict with id and name on success."""
        mock_stack_result = Stub()
        mock_stack_result.id = "stk-new"
        mock_openstack_connection.orchestration.create_stack.return_value = mock_stack_result

        template = "heat_template_version: 2021-04-16\nresources: {}"

        client = InfomaniakHeatClient(mock_openstack_connection)
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
        mock_openstack_connection.orchestration.create_stack.assert_called_once_with(
            name="fresh-stack",
            template=template,
            parameters={"image": "Ubuntu 22.04"},
            environment={"param_defaults": {}},
            timeout_mins=45,
            disable_rollback=True,
        )

    def test_create_stack_error_returns_none(self, mock_openstack_connection):
        """create_stack returns None on exception."""
        mock_openstack_connection.orchestration.create_stack.side_effect = Exception(
            "Quota exceeded"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.create_stack(name="fail-stack", template="bad")

        assert result is None

    def test_create_stack_from_file_success(self, mock_openstack_connection, tmp_path):
        """create_stack_from_file reads file and delegates to create_stack."""
        mock_stack_result = Stub()
        mock_stack_result.id = "stk-from-file"
        mock_openstack_connection.orchestration.create_stack.return_value = mock_stack_result

        template_content = "heat_template_version: 2021-04-16\nresources:\n  server:\n    type: OS::Nova::Server"
        template_file = tmp_path / "template.yaml"
        template_file.write_text(template_content)

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.create_stack_from_file(
            name="file-stack",
            template_path=str(template_file),
            parameters={"key_name": "ssh-key"},
        )

        assert result is not None
        assert result["id"] == "stk-from-file"
        mock_openstack_connection.orchestration.create_stack.assert_called_once()

    def test_create_stack_from_file_read_error(self, mock_openstack_connection):
        """create_stack_from_file returns None when file cannot be read."""
        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.create_stack_from_file(
            name="missing-file-stack",
            template_path="/nonexistent_path_xyz123/template.yaml",
        )

        assert result is None

    def test_update_stack_success(self, mock_openstack_connection):
        """update_stack returns True on successful update."""
        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.update_stack(
            stack_id="stk-upd",
            template="heat_template_version: 2021-04-16",
            parameters={"image": "Ubuntu 24.04"},
            environment={"resource_registry": {}},
        )

        assert result is True
        mock_openstack_connection.orchestration.update_stack.assert_called_once_with(
            "stk-upd",
            template="heat_template_version: 2021-04-16",
            parameters={"image": "Ubuntu 24.04"},
            environment={"resource_registry": {}},
        )

    def test_update_stack_error_returns_false(self, mock_openstack_connection):
        """update_stack returns False on exception."""
        mock_openstack_connection.orchestration.update_stack.side_effect = Exception(
            "Stack in DELETE_IN_PROGRESS"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.update_stack("stk-bad", template="new-template")

        assert result is False

    def test_delete_stack_success(self, mock_openstack_connection):
        """delete_stack returns True on successful deletion."""
        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.delete_stack("stk-del")

        assert result is True
        mock_openstack_connection.orchestration.delete_stack.assert_called_once_with("stk-del")

    def test_delete_stack_error_returns_false(self, mock_openstack_connection):
        """delete_stack returns False on exception."""
        mock_openstack_connection.orchestration.delete_stack.side_effect = Exception("Not found")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.delete_stack("stk-gone")

        assert result is False

    def test_suspend_stack_success(self, mock_openstack_connection):
        """suspend_stack returns True on success."""
        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.suspend_stack("stk-suspend")

        assert result is True
        mock_openstack_connection.orchestration.suspend_stack.assert_called_once_with(
            "stk-suspend"
        )

    def test_suspend_stack_error_returns_false(self, mock_openstack_connection):
        """suspend_stack returns False on exception."""
        mock_openstack_connection.orchestration.suspend_stack.side_effect = Exception(
            "Already suspended"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.suspend_stack("stk-already-sus")

        assert result is False

    def test_resume_stack_success(self, mock_openstack_connection):
        """resume_stack returns True on success."""
        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.resume_stack("stk-resume")

        assert result is True
        mock_openstack_connection.orchestration.resume_stack.assert_called_once_with(
            "stk-resume"
        )

    def test_resume_stack_error_returns_false(self, mock_openstack_connection):
        """resume_stack returns False on exception."""
        mock_openstack_connection.orchestration.resume_stack.side_effect = Exception(
            "Not suspended"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.resume_stack("stk-not-sus")

        assert result is False

    # =====================================================================
    # Stack Resources
    # =====================================================================

    def test_list_stack_resources_success(self, mock_openstack_connection):
        """list_stack_resources returns formatted resource dicts."""
        mock_resource = Stub()
        mock_resource.name = "my_server"
        mock_resource.resource_type = "OS::Nova::Server"
        mock_resource.status = "CREATE_COMPLETE"
        mock_resource.status_reason = "state changed"
        mock_resource.physical_resource_id = "srv-phys-001"

        mock_openstack_connection.orchestration.resources.return_value = [mock_resource]

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stack_resources("stk-res")

        assert len(result) == 1
        assert result[0]["name"] == "my_server"
        assert result[0]["resource_type"] == "OS::Nova::Server"
        assert result[0]["status"] == "CREATE_COMPLETE"
        assert result[0]["physical_resource_id"] == "srv-phys-001"
        mock_openstack_connection.orchestration.resources.assert_called_once_with("stk-res")

    def test_list_stack_resources_error_returns_empty(self, mock_openstack_connection):
        """list_stack_resources returns empty list on exception."""
        mock_openstack_connection.orchestration.resources.side_effect = Exception("Not found")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stack_resources("stk-bad")

        assert result == []

    def test_get_stack_resource_success(self, mock_openstack_connection):
        """get_stack_resource returns formatted dict for a single resource."""
        mock_resource = Stub()
        mock_resource.name = "my_network"
        mock_resource.resource_type = "OS::Neutron::Net"
        mock_resource.status = "CREATE_COMPLETE"
        mock_resource.physical_resource_id = "net-phys-002"
        mock_resource.attributes = {"admin_state_up": True}

        mock_openstack_connection.orchestration.get_resource.return_value = mock_resource

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_resource("stk-123", "my_network")

        assert result is not None
        assert result["name"] == "my_network"
        assert result["resource_type"] == "OS::Neutron::Net"
        assert result["attributes"]["admin_state_up"] is True
        mock_openstack_connection.orchestration.get_resource.assert_called_once_with(
            "stk-123", "my_network"
        )

    def test_get_stack_resource_error_returns_none(self, mock_openstack_connection):
        """get_stack_resource returns None on exception."""
        mock_openstack_connection.orchestration.get_resource.side_effect = Exception(
            "Resource not found"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_resource("stk-123", "nonexistent")

        assert result is None

    # =====================================================================
    # Stack Events
    # =====================================================================

    def test_list_stack_events_success(self, mock_openstack_connection):
        """list_stack_events returns formatted event dicts."""
        mock_event = Stub()
        mock_event.id = "evt-001"
        mock_event.resource_name = "my_server"
        mock_event.resource_status = "CREATE_COMPLETE"
        mock_event.resource_status_reason = "state changed"
        mock_event.event_time = "2026-01-15T10:30:00Z"

        mock_openstack_connection.orchestration.events.return_value = [mock_event]

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stack_events("stk-evt")

        assert len(result) == 1
        assert result[0]["id"] == "evt-001"
        assert result[0]["resource_name"] == "my_server"
        assert result[0]["resource_status"] == "CREATE_COMPLETE"
        assert result[0]["event_time"] == "2026-01-15T10:30:00Z"
        mock_openstack_connection.orchestration.events.assert_called_once_with("stk-evt", None)

    def test_list_stack_events_with_resource_filter(self, mock_openstack_connection):
        """list_stack_events passes resource_name filter to SDK."""
        mock_openstack_connection.orchestration.events.return_value = []

        client = InfomaniakHeatClient(mock_openstack_connection)
        client.list_stack_events("stk-evt", resource_name="my_server")

        mock_openstack_connection.orchestration.events.assert_called_once_with(
            "stk-evt", "my_server"
        )

    def test_list_stack_events_error_returns_empty(self, mock_openstack_connection):
        """list_stack_events returns empty list on exception."""
        mock_openstack_connection.orchestration.events.side_effect = Exception("Stack gone")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.list_stack_events("stk-gone")

        assert result == []

    # =====================================================================
    # Template Operations
    # =====================================================================

    def test_validate_template_success(self, mock_openstack_connection):
        """validate_template returns valid=True with description and parameters."""
        mock_openstack_connection.orchestration.validate_template.return_value = {
            "Description": "Web application stack",
            "Parameters": {
                "image": {"Type": "String", "Default": "Ubuntu 22.04"},
                "flavor": {"Type": "String", "Default": "a1-ram2-disk20-perf1"},
            },
        }

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.validate_template(
            template="heat_template_version: 2021-04-16",
            environment={"resource_registry": {}},
        )

        assert result["valid"] is True
        assert result["description"] == "Web application stack"
        assert "image" in result["parameters"]
        assert "flavor" in result["parameters"]
        mock_openstack_connection.orchestration.validate_template.assert_called_once_with(
            template="heat_template_version: 2021-04-16",
            environment={"resource_registry": {}},
        )

    def test_validate_template_failure(self, mock_openstack_connection):
        """validate_template returns valid=False with error on invalid template."""
        mock_openstack_connection.orchestration.validate_template.side_effect = Exception(
            "Invalid template: missing heat_template_version"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.validate_template(template="not: valid: yaml: garbage")

        assert result["valid"] is False
        assert "Invalid template" in result["error"]
        assert "heat_template_version" in result["error"]

    def test_get_stack_template_success(self, mock_openstack_connection):
        """get_stack_template returns template string on success."""
        expected_template = "heat_template_version: 2021-04-16\nresources:\n  server:\n    type: OS::Nova::Server"
        mock_openstack_connection.orchestration.get_stack_template.return_value = expected_template

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_template("stk-tmpl")

        assert result == expected_template
        mock_openstack_connection.orchestration.get_stack_template.assert_called_once_with(
            "stk-tmpl"
        )

    def test_get_stack_template_error_returns_none(self, mock_openstack_connection):
        """get_stack_template returns None on exception."""
        mock_openstack_connection.orchestration.get_stack_template.side_effect = Exception(
            "Stack not found"
        )

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_template("stk-missing")

        assert result is None

    # =====================================================================
    # Stack Outputs
    # =====================================================================

    def test_get_stack_outputs_with_outputs(self, mock_openstack_connection):
        """get_stack_outputs returns key-value dict from stack outputs."""
        stack = make_stub_stack(stack_id="stk-out")
        stack.outputs = [
            {"output_key": "public_ip", "output_value": "195.15.220.10"},
            {"output_key": "private_ip", "output_value": "10.0.0.5"},
            {"output_key": "url", "output_value": "https://app.example.com"},
        ]
        mock_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_outputs("stk-out")

        assert result["public_ip"] == "195.15.220.10"
        assert result["private_ip"] == "10.0.0.5"
        assert result["url"] == "https://app.example.com"
        assert len(result) == 3

    def test_get_stack_outputs_empty(self, mock_openstack_connection):
        """get_stack_outputs returns empty dict when stack has no outputs."""
        stack = make_stub_stack(stack_id="stk-no-out")
        stack.outputs = []
        mock_openstack_connection.orchestration.find_stack.return_value = stack

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_outputs("stk-no-out")

        assert result == {}

    def test_get_stack_outputs_stack_not_found(self, mock_openstack_connection):
        """get_stack_outputs returns empty dict when stack does not exist."""
        mock_openstack_connection.orchestration.find_stack.return_value = None

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_outputs("stk-gone")

        assert result == {}

    def test_get_stack_outputs_error_returns_empty(self, mock_openstack_connection):
        """get_stack_outputs returns empty dict on exception."""
        mock_openstack_connection.orchestration.find_stack.side_effect = Exception("Network error")

        client = InfomaniakHeatClient(mock_openstack_connection)
        result = client.get_stack_outputs("stk-err")

        assert result == {}


# =========================================================================

class TestInfomaniakHeatClientExpanded:
    """Tests for InfomaniakHeatClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient
        mock_conn = Stub()
        return InfomaniakHeatClient(connection=mock_conn), mock_conn

    def test_update_stack(self):
        """Test functionality: update stack."""
        client, mc = self._make_client()
        assert client.update_stack("stk1", template="heat: {}") is True
        mc.orchestration.update_stack.assert_called_once()

    def test_suspend_stack(self):
        """Test functionality: suspend stack."""
        client, mc = self._make_client()
        assert client.suspend_stack("stk1") is True
        mc.orchestration.suspend_stack.assert_called_once_with("stk1")

    def test_resume_stack(self):
        """Test functionality: resume stack."""
        client, mc = self._make_client()
        assert client.resume_stack("stk1") is True
        mc.orchestration.resume_stack.assert_called_once_with("stk1")

    def test_get_stack_resource(self):
        """Test functionality: get stack resource."""
        client, mc = self._make_client()
        res = Stub(name="srv", resource_type="OS::Nova::Server",
                        status="CREATE_COMPLETE", physical_resource_id="inst1",
                        attributes={"ip": "1.2.3.4"})
        mc.orchestration.get_resource.return_value = res
        result = client.get_stack_resource("stk1", "srv")
        assert result["resource_type"] == "OS::Nova::Server"

    def test_list_stack_events(self):
        """Test functionality: list stack events."""
        client, mc = self._make_client()
        ev = Stub(id="ev1", resource_name="srv",
                       resource_status="CREATE_COMPLETE",
                       resource_status_reason="OK", event_time=None)
        mc.orchestration.events.return_value = [ev]
        result = client.list_stack_events("stk1")
        assert len(result) == 1
        assert result[0]["resource_name"] == "srv"

    def test_get_stack_template(self):
        """Test functionality: get stack template."""
        client, mc = self._make_client()
        tpl = "heat_template_version: 2021-04-16"
        mc.orchestration.get_stack_template.return_value = tpl
        assert client.get_stack_template("stk1") == tpl

    def test_get_stack_outputs(self):
        """Test functionality: get stack outputs."""
        client, mc = self._make_client()
        stk = Stub()
        stk.outputs = [
            {"output_key": "server_ip", "output_value": "10.0.0.5"}
        ]
        mc.orchestration.find_stack.return_value = stk
        result = client.get_stack_outputs("stk1")
        assert result["server_ip"] == "10.0.0.5"

    def test_list_stacks_error(self):
        """Test functionality: list stacks error."""
        client, mc = self._make_client()
        mc.orchestration.stacks.side_effect = Exception("fail")
        assert client.list_stacks() == []


# =========================================================================
# ADDITIONAL METERING CLIENT TESTS
# =========================================================================
