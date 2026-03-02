"""Binary serialization formats implementation."""

import io
from typing import Any

import fastavro
import msgpack
import pandas as pd
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class MsgpackSerializer:
    """Msgpack serialization."""

    @staticmethod
    def serialize(data: Any) -> bytes:
        """Serialize this object to a portable format."""
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        return msgpack.unpackb(data, raw=False)

class AvroSerializer:
    """Avro serialization using fastavro."""

    @staticmethod
    def serialize(data: list[dict[str, Any]], schema: dict[str, Any]) -> bytes:
        """Serialize this object to a portable format."""
        out = io.BytesIO()
        fastavro.writer(out, schema, data)
        return out.getvalue()

    @staticmethod
    def deserialize(data: bytes) -> list[dict[str, Any]]:
        """Deserialize from a portable format and return an instance."""
        inp = io.BytesIO(data)
        reader = fastavro.reader(inp)
        return [record for record in reader]

class ParquetSerializer:
    """Parquet serialization using pandas and pyarrow."""

    @staticmethod
    def serialize(data: list[dict[str, Any]]) -> bytes:
        """Serialize this object to a portable format."""
        df = pd.DataFrame(data)
        out = io.BytesIO()
        df.to_parquet(out, engine='pyarrow')
        return out.getvalue()

    @staticmethod
    def deserialize(data: bytes) -> list[dict[str, Any]]:
        """Deserialize from a portable format and return an instance."""
        inp = io.BytesIO(data)
        df = pd.read_parquet(inp, engine='pyarrow')
        return df.to_dict('records')
