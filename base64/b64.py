import argparse
import base64
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Encode and decode base64 strings\n'
    )
    parser.add_argument('-d', '--decode',
                        dest='decode',
                        action='store_true',
                        default=False,
                        help='Decode data.\n'
                        )
    parser.add_argument('input', nargs='?')
    return parser.parse_args()


def main(args: argparse.Namespace):
    if not sys.stdin.isatty():
        from_input = "".join([line.rstrip() for line in sys.stdin.readlines()])
    elif args.input is None:
        sys.exit()
    else:
        from_input = args.input

    if args.decode:
        return base64.b64decode(from_input).decode()
    return base64.b64encode(from_input.encode()).decode()



if __name__ == '__main__':
    print(main(parse_args()), end='')
