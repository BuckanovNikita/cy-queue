"""Publish a metadata-only semantic release from the merged main branch.

The GitHub workflow owns merge authorization and serialization. This runner never
merges branches or overwrites remote history; its only push is an atomic commit/tag pair.
"""

import subprocess
import sys
import tomllib
from pathlib import Path

RELEASE_PATHS = {"pyproject.toml", "CHANGELOG.md"}
MAIN = "refs/heads/main"


def output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def remote_ref(ref: str) -> str:
    rows = output("git", "ls-remote", "--refs", "origin", ref).splitlines()
    if len(rows) > 1:
        raise ValueError(f"ambiguous remote ref: {ref}")
    return rows[0].split()[0] if rows else ""


def require_clean() -> None:
    if output("git", "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("release requires a clean checkout")
    if output("git", "symbolic-ref", "HEAD") != MAIN:
        raise ValueError("release requires main checked out")


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def validate_release(base: str, released: str) -> tuple[str, str]:
    if output("git", "rev-list", "--parents", "-n", "1", released) != f"{released} {base}":
        raise ValueError("semantic-release must create exactly one commit on the selected source")
    changed = set(output("git", "diff", "--name-only", base, released).splitlines())
    if not changed <= RELEASE_PATHS or "pyproject.toml" not in changed:
        raise ValueError(f"unexpected release paths: {sorted(changed)}")
    previous = tomllib.loads(output("git", "show", f"{base}:pyproject.toml"))["project"]["version"]
    version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    # Without its baseline tag semantic-release restarts from the first commit; a
    # hand-edited project.version runs ahead of the tags.
    if version_key(version) <= version_key(previous):
        raise ValueError(f"release {version} does not advance {previous}; check the latest tag and project.version")
    tag = f"v{version}"
    if output("git", "cat-file", "-t", f"refs/tags/{tag}") != "tag":
        raise ValueError("release tag must be annotated")
    if output("git", "rev-parse", f"refs/tags/{tag}^{{commit}}") != released:
        raise ValueError("release tag must target the release commit")
    return tag, output("git", "rev-parse", f"refs/tags/{tag}")


def release() -> None:
    if len(sys.argv) != 1:
        raise ValueError("releases run in GitHub Actions and accept no arguments")
    require_clean()
    # Refuse configuration that could publish to a different or multiple destinations.
    destination = output("git", "remote", "get-url", "origin")
    if output("git", "remote", "get-url", "--push", "--all", "origin").splitlines() != [destination]:
        raise ValueError("origin must have one identical fetch and push destination")
    run("git", "fetch", "--tags", "origin", f"{MAIN}:refs/remotes/origin/main")
    base = output("git", "rev-parse", "HEAD")
    if remote_ref(MAIN) != base:
        raise ValueError("checkout differs from remote main; rerun with a fresh checkout")
    run("semantic-release", "version", "--no-push", "--no-vcs-release")
    require_clean()
    released = output("git", "rev-parse", "HEAD")
    if remote_ref(MAIN) != base:
        raise ValueError("remote main moved during preparation; rerun with a fresh checkout")
    if released == base:
        print(f"No new version at {base}")
        return
    tag, identity = validate_release(base, released)
    if remote_ref(f"refs/tags/{tag}"):
        raise ValueError(f"remote tag {tag} already exists; refusing to replace it")
    run("git", "push", "--atomic", "--no-follow-tags", "origin", f"{released}:{MAIN}", f"{identity}:refs/tags/{tag}")
    if remote_ref(MAIN) != released or remote_ref(f"refs/tags/{tag}") != identity:
        raise ValueError("publication identity could not be confirmed; inspect remote refs before retrying")
    print(f"Published {tag}: commit {released}, annotated tag {identity}")


def main() -> int:
    try:
        release()
    except (KeyError, OSError, TypeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"release: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
