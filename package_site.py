#!/usr/bin/env python3
"""Copy only the public static website into the GitHub Pages artifact."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for item in ROOT.glob("*.html"):
        shutil.copy2(item, OUT / item.name)
    for name in (".nojekyll", "CNAME", "favicon.ico", "robots.txt", "sitemap.xml"):
        shutil.copy2(ROOT / name, OUT / name)
    for name in ("assets", "css", "js", "blog", "destinations", "trips", "preview"):
        if (ROOT / name).exists():
            shutil.copytree(ROOT / name, OUT / name)
    assert (OUT / "index.html").is_file()
    assert not (OUT / "data").exists(), "Release plans must not be served as website files"
    assert not (OUT / ".git").exists()
    print("Packaged public website into _site; release source data excluded.")


if __name__ == "__main__":
    main()
