## 📊 Database Integration

### **PostgreSQL Integration**

```python
# database_integration.py - PostgreSQL integration pattern
import asyncpg
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from codomyrmex.logging_monitoring import get_logger
import json

logger = get_logger(__name__)

class CodomyrmexDatabase:
    """PostgreSQL integration for Codomyrmex data persistence."""

    def __init__(self, database_url: str, pool_size: int = 10):
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool = None

    async def initialize(self):
        """Initialize database connection pool."""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=self.pool_size,
            command_timeout=60
        )

        # Create schema if it doesn't exist
        async with self.pool.acquire() as conn:
            await self._create_schema(conn)

        logger.info("Database pool initialized")

    async def _create_schema(self, conn):
        """Create database schema for Codomyrmex data."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS codomyrmex_jobs (
                id SERIAL PRIMARY KEY,
                job_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                input_data JSONB NOT NULL,
                result JSONB,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                execution_time_ms INTEGER
            );

            CREATE TABLE IF NOT EXISTS codomyrmex_analysis_cache (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(255) UNIQUE NOT NULL,
                content_hash VARCHAR(64) NOT NULL,
                analysis_result JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_jobs_status ON codomyrmex_jobs(status);
            CREATE INDEX IF NOT EXISTS idx_jobs_type ON codomyrmex_jobs(job_type);
            CREATE INDEX IF NOT EXISTS idx_cache_key ON codomyrmex_analysis_cache(cache_key);
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON codomyrmex_analysis_cache(expires_at);
        """)

    @asynccontextmanager
    async def transaction(self):
        """Database transaction context manager."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def store_job(self, job_type: str, input_data: Dict) -> int:
        """Store a new job in the database."""
        async with self.transaction() as conn:
            job_id = await conn.fetchval("""
                INSERT INTO codomyrmex_jobs (job_type, input_data)
                VALUES ($1, $2)
                RETURNING id
            """, job_type, json.dumps(input_data))

        logger.info(f"Stored job {job_id} of type {job_type}")
        return job_id

    async def update_job_result(self, job_id: int, result: Dict,
                               execution_time_ms: int, success: bool = True):
        """Update job with execution result."""
        status = 'completed' if success else 'failed'

        async with self.transaction() as conn:
            await conn.execute("""
                UPDATE codomyrmex_jobs
                SET status = $1, result = $2, execution_time_ms = $3,
                    updated_at = NOW()
                WHERE id = $4
            """, status, json.dumps(result), execution_time_ms, job_id)

        logger.info(f"Updated job {job_id} with status {status}")

    async def get_cached_analysis(self, cache_key: str) -> Optional[Dict]:
        """Get cached analysis result."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT analysis_result
                FROM codomyrmex_analysis_cache
                WHERE cache_key = $1 AND expires_at > NOW()
            """, cache_key)

        return json.loads(row['analysis_result']) if row else None

    async def store_cached_analysis(self, cache_key: str, content_hash: str,
                                  result: Dict, ttl_hours: int = 24):
        """Store analysis result in cache."""
        async with self.transaction() as conn:
            await conn.execute("""
                INSERT INTO codomyrmex_analysis_cache
                (cache_key, content_hash, analysis_result, expires_at)
                VALUES ($1, $2, $3, NOW() + INTERVAL '%d hours')
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    content_hash = EXCLUDED.content_hash,
                    analysis_result = EXCLUDED.analysis_result,
                    expires_at = EXCLUDED.expires_at
            """ % ttl_hours, cache_key, content_hash, json.dumps(result))

        logger.debug(f"Cached analysis result for key {cache_key}")

# Usage example with static analysis
async def analyze_codebase_with_db_cache(codebase_path: str,
                                       db: CodomyrmexDatabase) -> Dict:
    """Analyze codebase with database caching."""
    from codomyrmex.coding.static_analysis import analyze_codebase
    import hashlib

    # Generate cache key
    cache_key = f"static_analysis:{hashlib.md5(str(codebase_path).encode()).hexdigest()}"

    # Check cache first
    cached_result = await db.get_cached_analysis(cache_key)
    if cached_result:
        logger.info(f"Using cached analysis for {codebase_path}")
        return cached_result

    # Store job
    job_id = await db.store_job('static_analysis', {
        'codebase_path': str(codebase_path),
        'timestamp': time.time()
    })

    start_time = time.time()
    try:
        # Perform analysis
        result = analyze_codebase(codebase_path)
        execution_time = int((time.time() - start_time) * 1000)

        # Store results
        await db.update_job_result(job_id, result, execution_time, success=True)

        # Cache result
        content_hash = hashlib.md5(json.dumps(result, sort_keys=True).encode()).hexdigest()
        await db.store_cached_analysis(cache_key, content_hash, result)

        return result

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        error_result = {'error': str(e)}
        await db.update_job_result(job_id, error_result, execution_time, success=False)
        raise
```

### **MongoDB Integration**

```python
# mongodb_integration.py - MongoDB integration for flexible document storage
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import pymongo
from typing import Dict, List, Optional
from bson import ObjectId

class CodomyrmexMongoDB:
    """MongoDB integration for document-based data storage."""

    def __init__(self, connection_string: str, database_name: str = "codomyrmex"):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]

    async def initialize(self):
        """Initialize MongoDB collections and indexes."""
        # Create collections
        self.jobs = self.db.jobs
        self.analysis_results = self.db.analysis_results
        self.user_preferences = self.db.user_preferences

        # Create indexes
        await self.jobs.create_index([("status", 1), ("created_at", -1)])
        await self.jobs.create_index([("job_type", 1)])
        await self.analysis_results.create_index([("cache_key", 1)], unique=True)
        await self.analysis_results.create_index([("expires_at", 1)], expireAfterSeconds=0)

        logger.info("MongoDB collections and indexes initialized")

    async def store_analysis_result(self, analysis_type: str, input_data: Dict,
                                  result: Dict, ttl_hours: int = 24) -> str:
        """Store analysis result with automatic expiration."""
        doc = {
            'analysis_type': analysis_type,
            'input_data': input_data,
            'result': result,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=ttl_hours)
        }

        result_obj = await self.analysis_results.insert_one(doc)
        return str(result_obj.inserted_id)

    async def get_analysis_history(self, analysis_type: str = None,
                                 limit: int = 100) -> List[Dict]:
        """Get analysis history with optional filtering."""
        filter_query = {}
        if analysis_type:
            filter_query['analysis_type'] = analysis_type

        cursor = self.analysis_results.find(
            filter_query,
            sort=[('created_at', pymongo.DESCENDING)]
        ).limit(limit)

        return await cursor.to_list(length=limit)

    async def store_user_workflow(self, user_id: str, workflow_data: Dict) -> str:
        """Store user-specific workflow configuration."""
        doc = {
            'user_id': user_id,
            'workflow_data': workflow_data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Upsert based on user_id
        result = await self.user_preferences.replace_one(
            {'user_id': user_id},
            doc,
            upsert=True
        )

        return str(result.upserted_id or result.matched_count)

# Usage with AI code editing
async def ai_enhancement_with_history(code: str, user_id: str,
                                    mongo_db: CodomyrmexMongoDB):
    """AI code enhancement with history tracking."""
    from codomyrmex.agents import enhance_code

    # Enhance code
    result = await enhance_code(code, user_context=user_id)

    # Store in history
    await mongo_db.store_analysis_result(
        'ai_code_enhancement',
        {
            'user_id': user_id,
            'original_code': code,
            'enhancement_type': result.enhancement_type
        },
        {
            'enhanced_code': result.enhanced_code,
            'improvements': result.improvements,
            'confidence_score': result.confidence_score
        }
    )

    return result
```

