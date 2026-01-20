"""Binary serialization formats implementation."""

import msgpack
import fastavro
import pandas as pd
import io
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class MsgpackSerializer:
    """Msgpack serialization."""
    
    @staticmethod
    def serialize(data: Any) -> bytes:
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def deserialize(data: bytes) -> Any:
        return msgpack.unpackb(data, raw=False)

class AvroSerializer:
    """Avro serialization using fastavro."""
    
    @staticmethod
    def serialize(data: List[Dict[str, Any]], schema: Dict[str, Any]) -> bytes:
        out = io.BytesIO()
        fastavro.writer(out, schema, data)
        return out.getvalue()

    @staticmethod
    def deserialize(data: bytes) -> List[Dict[str, Any]]:
        inp = io.BytesIO(data)
        reader = fastavro.reader(inp)
        return [record for record in reader]

class ParquetSerializer:
    """Parquet serialization using pandas and pyarrow."""
    
    @staticmethod
    def serialize(data: List[Dict[str, Any]]) -> bytes:
        df = pd.DataFrame(data)
        out = io.BytesIO()
        df.to_parquet(out, engine='pyarrow')
        return out.getvalue()

    @staticmethod
    def deserialize(data: bytes) -> List[Dict[str, Any]]:
        inp = io.BytesIO(data)
        df = pd.read_parquet(inp, engine='pyarrow')
        return df.to_dict('records')
