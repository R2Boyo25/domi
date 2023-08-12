import subprocess
import os


def generate_protobuf(setup_kwargs):
    subprocess.run(
        [
            "protoc",
            "--python_out=domi",
            *map(
                lambda x: "pbuf/" + x,
                filter(lambda x: "~" not in x, os.listdir("pbuf")),
            ),
        ]
    )
    return setup_kwargs


if __name__ == "__main__":
    generate_protobuf({})
