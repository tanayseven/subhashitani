import sys
from argparse import ArgumentParser
from pathlib import Path

import frontmatter


def validate() -> None:
    errors: list[str] = []
    seen_slugs: dict[str, Path] = {}
    required_fields = ("slug", "title", "source", "date")

    for path in sorted(Path("content").rglob("*.md")):
        post = frontmatter.load(str(path))
        meta = post.metadata

        for field in required_fields:
            if field not in meta:
                errors.append(f"{path}: missing required field '{field}'")

        slug = meta.get("slug")
        if slug:
            if slug in seen_slugs:
                errors.append(
                    f"{path}: duplicate slug '{slug}' (first seen in {seen_slugs[slug]})"
                )
            else:
                seen_slugs[slug] = path

        tags = meta.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"{path}: 'tags' must be a list, got {type(tags).__name__}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: validated {len(seen_slugs)} shloka(s)")


def build() -> None:
    from app import freeze
    freeze()


def main() -> None:
    parser = ArgumentParser(prog="cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate all shloka markdown files")
    subparsers.add_parser("build", help="Freeze Flask app into static files")

    args = parser.parse_args()
    if args.command == "validate":
        validate()
    elif args.command == "build":
        build()


if __name__ == "__main__":
    main()