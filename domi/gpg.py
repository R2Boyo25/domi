import os
import pathlib
import tempfile
import subprocess

import gnupg


def create_context(gnupghome: str, keyring: str | None = None):
    if not os.path.exists(gnupghome):
        os.mkdir(gnupghome)

    return gnupg.GPG(gnupghome=gnupghome, keyring=keyring)


def get_gpghome() -> str:
    path = GNUPGHOME = pathlib.Path(os.getenv("XDG_RUNTIME_DIR", "/tmp")) / "domi_gpg"
    path.mkdir(exist_ok=True, mode=0o700)
    return path


def mktempfile(content: str | bytes | None = None) -> tempfile.TemporaryFile:
    temporary_file = tempfile.NamedTemporaryFile(
        dir=os.getenv("XDG_RUNTIME_DIR", "/tmp")
    )

    if content is not None:
        temporary_file.write(content)
        temporary_file.flush()
        temporary_file.seek(0)

    print(temporary_file.name)
    print(temporary_file.read())
    temporary_file.seek(0)
        
    return temporary_file


def import_key(key: bytes) -> None:
    with mktempfile(key) as stdin:
        home = get_gpghome()

        subprocess.run(
            ["gpg", "--import"],
            stdin=stdin,
            env=dict(os.environ, GNUPGHOME=home)
        )
    

def encrypt(
    content: bytes, recipient_keys: list[bytes] = [], sign=False
) -> bytes:
    with mktempfile(content) as stdin:
        tempfiles = [mktempfile(key) for key in recipient_keys]

        options = []

        for temporary_file in tempfiles:
            options.extend(["--recipient-file", temporary_file.name])

        result = subprocess.check_output(
            ["gpg"]
            + (["--sign"] if sign else [])
            + ["--encrypt", *options],
            stdin=stdi,n
            env=dict(os.environ, GNUPGHOME=get_gpghome()),
        )

        for file in tempfiles:
            file.close()

        return result


def verify(signed_content: bytes, signer_keys: list[bytes] = []) -> bool:
    with mktempfile(signed_content) as stdin:
        tempfiles = [mktempfile(key) for key in signer_keys]

        options = []

        for temporary_file in tempfiles:
            options.extend(["--keyring", temporary_file.name])

        result = (
            subprocess.run(
                ["gpgv", "--ignore-time-conflict", "--output", "-", *options],
                stdin=stdin,
                env=dict(os.environ, GNUPGHOME=get_gpghome()),
            ).returncode
            == 0
        )

        for file in tempfiles:
            file.close()

        return result


def decrypt(encrypted_content):
    with mktempfile(encrypted_content) as stdin:
        return subprocess.check_output(
            ["gpg", "--decrypt"],
            stdin=stdin,
            env=dict(os.environ, GNUPGHOME=get_gpghome()),
        )


class GPGContext:
    def __init__(self, keyring_name: str):
        self.gnupghome = os.getenv("DOMI_GPGHOME", "/data/")
        self.keyring_name = keyring_name
        self.ctx = create_context(self.gnupghome)

    def import_key(self, key: str) -> str:
        return self.ctx.import_keys(key).fingerprints[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        (pathlib.Path(self.gnupghome) / f"{self.keyring_name}.gpg").unlink(
            missing_ok=True
        )
        del self
