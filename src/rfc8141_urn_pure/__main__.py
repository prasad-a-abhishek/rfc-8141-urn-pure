"""CLI entry point for rfc8141-urn-pure.

Usage:
    urn parse <urn-string>
    urn validate <urn-string>
    urn construct <nid> <nss>
    urn resolve-ni <urn-string>
    urn resolve-tag <urn-string>
    urn --help
    urn --version
"""
from __future__ import annotations

import argparse
import json
import sys

from rfc8141_urn_pure import (
    parse,
    validate,
    construct,
    resolve_ni,
    resolve_tag,
    Urn,
    URNParsingError,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on error."""
    parser = argparse.ArgumentParser(
        prog="urn",
        description="RFC 8141 URN parser, validator, constructor, and resolver",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="urn 0.1.0 (rfc8141-urn-pure)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # urn parse <urn-string>
    p_parse = sub.add_parser("parse", help="Parse a URN string and print components as JSON")
    p_parse.add_argument("urn", help="URN string to parse")

    # urn validate <urn-string>
    p_valid = sub.add_parser("validate", help="Validate a URN string; exit 0 if valid, 1 if invalid")
    p_valid.add_argument("urn", help="URN string to validate")

    # urn construct <nid> <nss>
    p_const = sub.add_parser("construct", help="Construct a URN from NID and NSS")
    p_const.add_argument("nid", help="Namespace Identifier (2-32 chars)")
    p_const.add_argument("nss", help="Namespace Specific String")
    p_const.add_argument(
        "--percent-encode",
        action="store_true",
        help="Percent-encode the NSS before assembly",
    )

    # urn resolve-ni <urn-string>
    p_ni = sub.add_parser(
        "resolve-ni",
        help="Resolve a ni: URN (RFC 6920) and print hash digest",
    )
    p_ni.add_argument("urn", help="ni: URN string to resolve")

    # urn resolve-tag <urn-string>
    p_tag = sub.add_parser(
        "resolve-tag",
        help="Resolve a tag: URN (RFC 4151) and print tag string",
    )
    p_tag.add_argument("urn", help="tag: URN string to resolve")

    args = parser.parse_args(argv)

    try:
        if args.command == "parse":
            urn_obj = parse(args.urn)
            output = {
                "nid": urn_obj.nid,
                "nss": urn_obj.nss,
                "nss_decoded": urn_obj.nss_decoded,
                "rqn": urn_obj.rqn,
                "original": urn_obj.original,
            }
            print(json.dumps(output, indent=2))
            return 0

        elif args.command == "validate":
            if validate(args.urn):
                print("valid")
                return 0
            else:
                print("invalid")
                return 1

        elif args.command == "construct":
            result = construct(args.nid, args.nss, percent_encode=args.percent_encode)
            print(result)
            return 0

        elif args.command == "resolve-ni":
            result = resolve_ni(args.urn)
            if result is None:
                print("null")
                return 0
            print(result.hex())
            return 0

        elif args.command == "resolve-tag":
            result = resolve_tag(args.urn)
            print(result)
            return 0

        else:
            parser.print_help()
            return 1

    except URNParsingError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Total-over-input: catch any unexpected exception
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
