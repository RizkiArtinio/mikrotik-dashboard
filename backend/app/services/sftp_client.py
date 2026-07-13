"""Shared SFTP helper for pulling files off a router's filesystem.

RouterOS's API has no "download file contents" command, so backups and
exported certificates can only be retrieved via SFTP (using router.ssh_port,
which defaults to 22 but is commonly moved to a custom port on hardened
setups).
"""

import io

import paramiko

from app.core.crypto import decrypt_secret
from app.models.router import Router


def fetch_to_path(router: Router, remote_filename: str, local_path: str) -> None:
    transport = paramiko.Transport((router.ip_address, router.ssh_port))
    try:
        transport.connect(username=router.username, password=decrypt_secret(router.password_encrypted))
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(remote_filename, local_path)
        finally:
            sftp.close()
    finally:
        transport.close()


def fetch_to_text(router: Router, remote_filename: str) -> str:
    transport = paramiko.Transport((router.ip_address, router.ssh_port))
    try:
        transport.connect(username=router.username, password=decrypt_secret(router.password_encrypted))
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            buffer = io.BytesIO()
            sftp.getfo(remote_filename, buffer)
            return buffer.getvalue().decode()
        finally:
            sftp.close()
    finally:
        transport.close()


def remove_remote_file(router: Router, remote_filename: str) -> None:
    transport = paramiko.Transport((router.ip_address, router.ssh_port))
    try:
        transport.connect(username=router.username, password=decrypt_secret(router.password_encrypted))
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.remove(remote_filename)
        finally:
            sftp.close()
    finally:
        transport.close()
