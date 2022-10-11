import sys


def pre(label: str) -> str:
    return f"-----BEGIN {label}-----\n"


def post(label: str) -> str:
    return f"-----END {label}-----"


base64 = "".join(sys.stdin.readlines())
print(pre("CERTIFICATE") + base64 + post("CERTIFICATE"))
