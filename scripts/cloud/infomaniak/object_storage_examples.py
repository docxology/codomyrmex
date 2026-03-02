#!/usr/bin/env python3
"""
Infomaniak Object Storage Examples.

Demonstrates both Swift and S3-compatible storage clients:
- InfomaniakObjectStorageClient (Swift)
- InfomaniakS3Client (S3-compatible)

Usage:
    # Swift operations
    python object_storage_examples.py --swift --list-containers
    python object_storage_examples.py --swift --list-objects my-container
    
    # S3 operations
    python object_storage_examples.py --s3 --list-buckets
    python object_storage_examples.py --s3 --upload --bucket my-bucket --key test.txt --file local.txt
    python object_storage_examples.py --s3 --download --bucket my-bucket --key test.txt --output downloaded.txt
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_swift_client():
    """Get Swift client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakObjectStorageClient
    return InfomaniakObjectStorageClient.from_env()


def get_s3_client():
    """Get S3 client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakS3Client
    return InfomaniakS3Client.from_env()


# =========================================================================
# Swift Operations
# =========================================================================

def swift_list_containers(client):
    """List Swift containers."""
    print("\n📦 Swift Containers\n" + "=" * 50)
    containers = client.list_containers()
    
    if not containers:
        print("   No containers found.")
        return
    
    for name in containers:
        print(f"   📁 {name}")


def swift_list_objects(client, container: str, prefix: str = None):
    """List objects in a Swift container."""
    print(f"\n📄 Objects in '{container}'\n" + "=" * 50)
    objects = client.list_objects(container, prefix=prefix)
    
    if not objects:
        print("   No objects found.")
        return
    
    for name in objects:
        print(f"   📄 {name}")


def swift_upload(client, container: str, name: str, file_path: str):
    """Upload a file to Swift."""
    print(f"\n⬆️  Uploading to {container}/{name}")
    
    if client.upload_file(container, name, file_path):
        print("   ✅ Upload successful")
    else:
        print("   ❌ Upload failed")


def swift_download(client, container: str, name: str, output_path: str):
    """Download an object from Swift."""
    print(f"\n⬇️  Downloading {container}/{name}")
    
    if client.download_file(container, name, output_path):
        print(f"   ✅ Downloaded to {output_path}")
    else:
        print("   ❌ Download failed")


def swift_create_container(client, name: str):
    """Create a Swift container."""
    print(f"\n📦 Creating container: {name}")
    
    if client.create_container(name):
        print("   ✅ Container created")
    else:
        print("   ❌ Failed to create container")


# =========================================================================
# S3 Operations
# =========================================================================

def s3_list_buckets(client):
    """List S3 buckets."""
    print("\n🪣 S3 Buckets\n" + "=" * 50)
    buckets = client.list_buckets()
    
    if not buckets:
        print("   No buckets found.")
        return
    
    for name in buckets:
        print(f"   🪣 {name}")


def s3_list_objects(client, bucket: str, prefix: str = None):
    """List objects in an S3 bucket."""
    print(f"\n📄 Objects in '{bucket}'\n" + "=" * 50)
    objects = client.list_objects(bucket, prefix=prefix)
    
    if not objects:
        print("   No objects found.")
        return
    
    for key in objects:
        print(f"   📄 {key}")


def s3_upload(client, bucket: str, key: str, file_path: str):
    """Upload a file to S3."""
    print(f"\n⬆️  Uploading to s3://{bucket}/{key}")
    
    if client.upload_file(bucket, key, file_path):
        print("   ✅ Upload successful")
    else:
        print("   ❌ Upload failed")


def s3_upload_data(client, bucket: str, key: str, data: str, content_type: str = None):
    """Upload data directly to S3."""
    print(f"\n⬆️  Uploading data to s3://{bucket}/{key}")
    
    if client.upload_data(bucket, key, data.encode(), content_type):
        print("   ✅ Upload successful")
    else:
        print("   ❌ Upload failed")


def s3_download(client, bucket: str, key: str, output_path: str):
    """Download an object from S3."""
    print(f"\n⬇️  Downloading s3://{bucket}/{key}")
    
    if client.download_file(bucket, key, output_path):
        print(f"   ✅ Downloaded to {output_path}")
    else:
        print("   ❌ Download failed")


def s3_create_bucket(client, name: str):
    """Create an S3 bucket."""
    print(f"\n🪣 Creating bucket: {name}")
    
    if client.create_bucket(name):
        print("   ✅ Bucket created")
    else:
        print("   ❌ Failed to create bucket")


def s3_get_metadata(client, bucket: str, key: str):
    """Get object metadata."""
    print(f"\n📋 Metadata for s3://{bucket}/{key}\n" + "=" * 50)
    meta = client.get_metadata(bucket, key)
    
    if meta:
        for k, v in meta.items():
            print(f"   {k}: {v}")
    else:
        print("   Object not found or error")


def s3_presigned_url(client, bucket: str, key: str, expires: int):
    """Generate a presigned URL."""
    print(f"\n🔗 Generating presigned URL for s3://{bucket}/{key}")
    
    url = client.generate_presigned_url(bucket, key, expires_in=expires)
    if url:
        print(f"   ✅ URL (expires in {expires}s):")
        print(f"   {url}")
    else:
        print("   ❌ Failed to generate URL")


def s3_delete(client, bucket: str, key: str):
    """Delete an S3 object."""
    print(f"\n🗑️  Deleting s3://{bucket}/{key}")
    
    if client.delete_object(bucket, key):
        print("   ✅ Object deleted")
    else:
        print("   ❌ Failed to delete object")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Object Storage Examples")
    
    # Client selection
    parser.add_argument("--swift", action="store_true", help="Use Swift client")
    parser.add_argument("--s3", action="store_true", help="Use S3 client")
    
    # List operations
    parser.add_argument("--list-containers", action="store_true", help="List Swift containers")
    parser.add_argument("--list-buckets", action="store_true", help="List S3 buckets")
    parser.add_argument("--list-objects", type=str, metavar="CONTAINER/BUCKET", help="List objects")
    
    # CRUD operations
    parser.add_argument("--upload", action="store_true", help="Upload file")
    parser.add_argument("--upload-data", type=str, metavar="DATA", help="Upload raw data")
    parser.add_argument("--download", action="store_true", help="Download object")
    parser.add_argument("--delete", action="store_true", help="Delete object")
    parser.add_argument("--create-container", type=str, metavar="NAME", help="Create container")
    parser.add_argument("--create-bucket", type=str, metavar="NAME", help="Create bucket")
    
    # Other operations
    parser.add_argument("--metadata", action="store_true", help="Get object metadata")
    parser.add_argument("--presigned-url", action="store_true", help="Generate presigned URL")
    
    # Options
    parser.add_argument("--bucket", type=str, help="Bucket name")
    parser.add_argument("--container", type=str, help="Container name")
    parser.add_argument("--key", type=str, help="Object key")
    parser.add_argument("--file", type=str, help="Local file path")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--prefix", type=str, help="Object prefix filter")
    parser.add_argument("--content-type", type=str, help="Content type")
    parser.add_argument("--expires", type=int, default=3600, help="URL expiration seconds")
    
    args = parser.parse_args()
    
    # Determine client type
    if args.swift:
        try:
            client = get_swift_client()
            client_type = "swift"
        except Exception as e:
            print(f"❌ Failed to create Swift client: {e}")
            return 1
    elif args.s3:
        try:
            client = get_s3_client()
            client_type = "s3"
        except Exception as e:
            print(f"❌ Failed to create S3 client: {e}")
            return 1
    else:
        print("❌ Specify --swift or --s3")
        parser.print_help()
        return 1
    
    # Execute operations
    if args.list_containers and client_type == "swift":
        swift_list_containers(client)
    elif args.list_buckets and client_type == "s3":
        s3_list_buckets(client)
    elif args.list_objects:
        if client_type == "swift":
            swift_list_objects(client, args.list_objects, args.prefix)
        else:
            s3_list_objects(client, args.list_objects, args.prefix)
    elif args.upload:
        if not args.file:
            print("❌ --upload requires --file")
            return 1
        if client_type == "swift":
            if not args.container or not args.key:
                print("❌ --upload requires --container and --key")
                return 1
            swift_upload(client, args.container, args.key, args.file)
        else:
            if not args.bucket or not args.key:
                print("❌ --upload requires --bucket and --key")
                return 1
            s3_upload(client, args.bucket, args.key, args.file)
    elif args.upload_data and client_type == "s3":
        if not args.bucket or not args.key:
            print("❌ --upload-data requires --bucket and --key")
            return 1
        s3_upload_data(client, args.bucket, args.key, args.upload_data, args.content_type)
    elif args.download:
        if not args.output:
            print("❌ --download requires --output")
            return 1
        if client_type == "swift":
            if not args.container or not args.key:
                print("❌ --download requires --container and --key")
                return 1
            swift_download(client, args.container, args.key, args.output)
        else:
            if not args.bucket or not args.key:
                print("❌ --download requires --bucket and --key")
                return 1
            s3_download(client, args.bucket, args.key, args.output)
    elif args.delete and client_type == "s3":
        if not args.bucket or not args.key:
            print("❌ --delete requires --bucket and --key")
            return 1
        s3_delete(client, args.bucket, args.key)
    elif args.create_container and client_type == "swift":
        swift_create_container(client, args.create_container)
    elif args.create_bucket and client_type == "s3":
        s3_create_bucket(client, args.create_bucket)
    elif args.metadata and client_type == "s3":
        if not args.bucket or not args.key:
            print("❌ --metadata requires --bucket and --key")
            return 1
        s3_get_metadata(client, args.bucket, args.key)
    elif args.presigned_url and client_type == "s3":
        if not args.bucket or not args.key:
            print("❌ --presigned-url requires --bucket and --key")
            return 1
        s3_presigned_url(client, args.bucket, args.key, args.expires)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
