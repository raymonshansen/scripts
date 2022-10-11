import sys
import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Wrap a PEM certificate in header and footer\n'
    )
    parser.add_argument('input', nargs='?')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    if not sys.stdin.isatty():
        from_input = sys.stdin.read()
    elif args.input is None:
        sys.exit()
    else:
        from_input = args.input + "\n"

    print(f"""
-----BEGIN CERTIFICATE-----
{from_input}-----END CERTIFICATE-----
""")
