"""
ConfigDiff CLI - Command-line interface.
"""
import sys
import argparse
from pathlib import Path


def build_parser():
    p = argparse.ArgumentParser(
        prog="configdiff",
        description="ConfigDiff - Multi-format configuration file diff tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  configdiff file_a.yaml file_b.yaml
  configdiff app_config.json prod_config.json --format=json
  configdiff dir_a/ dir_b/ --recursive --format=markdown --output=report.md
  configdiff .env.staging .env.prod --color=never
  configdiff file_a.toml file_b.toml --ignore-order
        """
    )
    p.add_argument("left", nargs="?", help="Left file or directory")
    p.add_argument("right", nargs="?", help="Right file or directory")
    p.add_argument("-o", "--output", dest="output_file", help="Output file (default: stdout)")
    p.add_argument("-f", "--format", dest="output_format", default="color",
                  choices=["color", "plain", "text", "json", "markdown", "md", "git"],
                  help="Output format (default: color)")
    p.add_argument("-c", "--context", type=int, default=3,
                  help="Context lines around changes (default: 3)")
    p.add_argument("--ignore-order", action="store_true",
                  help="Ignore ordering differences in arrays")
    p.add_argument("--ignore-comments", action="store_true",
                  help="Ignore comment lines")
    p.add_argument("--color", dest="color", default="auto",
                  choices=["auto", "always", "never"],
                  help="Force color output (default: auto)")
    p.add_argument("-r", "--recursive", action="store_true",
                  help="Recursively compare directories")
    p.add_argument("-p", "--pattern", default="*",
                  help="File pattern for directory diff (default: *)")
    p.add_argument("-q", "--quiet", action="store_true",
                  help="Only output summary, no diff content")
    p.add_argument("--version", action="version", version="ConfigDiff 1.0.0")
    return p


def cmd_diff(args):
    from configdiff import ConfigDiff

    cd = ConfigDiff(ignore_order=args.ignore_order, ignore_comments=args.ignore_comments)

    left = Path(args.left) if args.left else None
    right = Path(args.right) if args.right else None

    if left and right and left.is_dir() and right.is_dir():
        results = cd.diff_dir(left, right, pattern=args.pattern,
                              recursive=args.recursive, format=args.output_format)
        output_lines = []
        for path, result in results.items():
            if result is None:
                output_lines.append(f"Error comparing: {path}")
                continue
            if result.changed:
                output_lines.append(cd.format(result, format=args.output_format))
                output_lines.append("")
        if not output_lines:
            output_lines = ["No differences found."]
        content = "\n".join(output_lines)
    elif left and right and left.is_file() and right.is_file():
        result = cd.diff_file(left, right, context=args.context)
        if args.quiet:
            content = f"{result.stats['added']} added, {result.stats['removed']} removed"
        else:
            content = cd.format(result, format=args.output_format)
    elif left and right:
        try:
            l = Path(left).read_text(encoding="utf-8", errors="replace") if Path(left).exists() else str(left)
            r = Path(right).read_text(encoding="utf-8", errors="replace") if Path(right).exists() else str(right)
            result = cd.diff_strings(l, r, context=args.context)
            content = cd.format(result, format=args.output_format)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if left:
            content = f"Comparing stdin with: {left}"
        else:
            print("Usage: configdiff <file_a> <file_b>")
            sys.exit(1)

    if args.output_file:
        Path(args.output_file).write_text(content, encoding="utf-8")
        print(f"Written to {args.output_file}")
    else:
        if args.color == "never":
            from configdiff.formatters import Colors
            content = Colors.strip(content)
        print(content)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.left and sys.stdin.isatty():
        parser.print_help()
        return

    try:
        cmd_diff(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
