"""ElementsMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    Control,
    ControlList,
    Formula,
    FormulaList,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class ElementsMixin:
    """ElementsMixin class."""

    def push_button(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_id_or_name: str,
        column_id_or_name: str,
    ) -> dict[str, Any]:
        """
        Push a button in a table.

        The button can perform any action on the document.

        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_id_or_name: Row ID or name
            column_id_or_name: Column ID or name of the button

        Returns:
            Result with request_id
        """
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/rows/{self._encode_id(row_id_or_name)}"
            f"/buttons/{self._encode_id(column_id_or_name)}"
        )
        return self._post(path)

    def list_formulas(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: str | None = None,
        sort_by: str | None = None,
    ) -> FormulaList:
        """
        List named formulas in a doc.

        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            sort_by: Sort order ("name")

        Returns:
            FormulaList with items
        """
        params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
        path = f"/docs/{self._encode_id(doc_id)}/formulas"
        data = self._get(path, params=params)
        return FormulaList.from_dict(data)

    def get_formula(self, doc_id: str, formula_id_or_name: str) -> Formula:
        """
        Get a formula's current value.

        Args:
            doc_id: The doc ID
            formula_id_or_name: Formula ID or name

        Returns:
            Formula with computed value
        """
        path = f"/docs/{self._encode_id(doc_id)}/formulas/{self._encode_id(formula_id_or_name)}"
        data = self._get(path)
        return Formula.from_dict(data)

    def list_controls(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: str | None = None,
        sort_by: str | None = None,
    ) -> ControlList:
        """
        List controls in a doc.

        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            sort_by: Sort order ("name")

        Returns:
            ControlList with items
        """
        params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
        path = f"/docs/{self._encode_id(doc_id)}/controls"
        data = self._get(path, params=params)
        return ControlList.from_dict(data)

    def get_control(self, doc_id: str, control_id_or_name: str) -> Control:
        """
        Get a control's current value.

        Args:
            doc_id: The doc ID
            control_id_or_name: Control ID or name

        Returns:
            Control with current value
        """
        path = f"/docs/{self._encode_id(doc_id)}/controls/{self._encode_id(control_id_or_name)}"
        data = self._get(path)
        return Control.from_dict(data)

    def trigger_automation(
        self,
        doc_id: str,
        rule_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Trigger a webhook automation.

        Args:
            doc_id: The doc ID
            rule_id: The automation rule ID
            payload: Payload to send to the webhook

        Returns:
            Result with request_id
        """
        path = f"/docs/{self._encode_id(doc_id)}/hooks/automation/{self._encode_id(rule_id)}"
        return self._post(path, json_data=payload or {})

