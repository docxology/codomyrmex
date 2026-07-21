"""SSH and SFTP client implementation."""

import paramiko

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SSHClient:
    """Wrapper for SSH operations using Paramiko."""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str | None = None,
        key_filename: str | None = None,
        port: int = 22,
        known_hosts_file: str | None = None,
        allow_unknown_host_keys: bool = False,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.allow_unknown_host_keys = allow_unknown_host_keys
        self.client = paramiko.SSHClient()
        # Load known hosts and reject anything that is not explicitly trusted.
        if known_hosts_file:
            self.client.load_host_keys(known_hosts_file)
        else:
            self.client.load_system_host_keys()
        if allow_unknown_host_keys:
            # This compatibility escape hatch is deliberately explicit. It
            # accepts unknown keys and must never be the secure default.
            logger.warning(
                "SSH unknown host keys are accepted for %s; this is unsafe "
                "and vulnerable to man-in-the-middle attacks",
                hostname,
            )
            self.client.set_missing_host_key_policy(  # nosec B507 - explicit unsafe opt-in
                paramiko.WarningPolicy()
            )
        else:
            self.client.set_missing_host_key_policy(paramiko.RejectPolicy())

    def connect(self) -> None:
        """Establish SSH connection."""
        self.client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename,
        )
        logger.info("Connected to %s@%s:%s", self.username, self.hostname, self.port)

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """Execute a command on the remote host."""
        _stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        return exit_status, stdout.read().decode(), stderr.read().decode()

    def get_sftp(self) -> paramiko.SFTPClient:
        """Get an SFTP client instance."""
        return self.client.open_sftp()

    def close(self) -> None:
        """Close the SSH connection."""
        self.client.close()
        logger.info("Closed connection to %s", self.hostname)

    def __enter__(self):
        """Enter the context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up."""
        self.close()
