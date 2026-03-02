"""SSH and SFTP client implementation."""

import paramiko

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class SSHClient:
    """Wrapper for SSH operations using Paramiko."""

    def __init__(self, hostname: str, username: str, password: str | None = None, key_filename: str | None = None, port: int = 22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self) -> None:
        """Establish SSH connection."""
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename
        )
        logger.info(f"Connected to {self.username}@{self.hostname}:{self.port}")

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """Execute a command on the remote host."""
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        return exit_status, stdout.read().decode(), stderr.read().decode()

    def get_sftp(self) -> paramiko.SFTPClient:
        """Get an SFTP client instance."""
        return self.client.open_sftp()

    def close(self) -> None:
        """Close the SSH connection."""
        self.client.close()
        logger.info(f"Closed connection to {self.hostname}")

    def __enter__(self):
        """Enter the context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up."""
        self.close()
