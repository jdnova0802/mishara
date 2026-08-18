#!/usr/bin/env python3
"""Gate CLI — hop, lookup, me from terminal."""
import argparse
import json
import os
import sys

try:
    from gate.sdk.gate_client import GateClient, GateError
except ImportError:
    from sdk.gate_client import GateClient, GateError


def main():
    parser = argparse.ArgumentParser(description="Gate API CLI")
    parser.add_argument("--key", default=os.getenv("GATE_API_KEY"), help="gate_sk_live_...")
    parser.add_argument("--base", default=os.getenv("GATE_API_URL", "http://localhost:5001"))
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lookup = sub.add_parser("lookup", help="Fuse existence lookup")
    p_lookup.add_argument("fuse_id")

    p_hop = sub.add_parser("hop", help="Pre-exec fuse hop")
    p_hop.add_argument("fuse_id")

    p_pc = sub.add_parser("pre-bind", help="PolicyCenter pre-bind weld")
    p_pc.add_argument("fuse_id")
    p_pc.add_argument("job_id")

    p_mga = sub.add_parser("mga", help="MGA authority check")
    p_mga.add_argument("fuse_id")
    p_mga.add_argument("--premium", type=float)
    p_mga.add_argument("--limit", type=float, dest="authority_limit")
    p_mga.add_argument("--line")
    p_mga.add_argument("--state")

    sub.add_parser("appendix", help="On-request bind appendix for this key")

    sub.add_parser("me", help="Key metadata + usage")

    p_demo = sub.add_parser("demo-hop", help="Execute gate demo")
    args = parser.parse_args()

    if not args.key and args.cmd != "demo-hop":
        print("Set GATE_API_KEY or pass --key", file=sys.stderr)
        sys.exit(1)

    client = GateClient(api_key=args.key or "unused", base_url=args.base)
    try:
        if args.cmd == "lookup":
            out = client.lookup(args.fuse_id)
        elif args.cmd == "hop":
            out = client.hop(args.fuse_id)
        elif args.cmd == "pre-bind":
            out = client.policycenter_pre_bind(args.fuse_id, args.job_id)
        elif args.cmd == "mga":
            extra = {}
            if args.premium is not None:
                extra["premium"] = args.premium
            if args.authority_limit is not None:
                extra["authority_limit"] = args.authority_limit
            if args.line:
                extra["line"] = args.line
            if args.state:
                extra["state"] = args.state
            out = client.mga_authority(args.fuse_id, **extra)
        elif args.cmd == "appendix":
            out = client.bind_appendix()
        elif args.cmd == "me":
            out = client.me()
        elif args.cmd == "demo-hop":
            out = client.execute_gate_demo()
        else:
            parser.print_help()
            sys.exit(1)
        print(json.dumps(out, indent=2))
    except GateError as e:
        print(json.dumps(e.payload or {"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
