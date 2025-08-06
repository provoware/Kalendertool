# =========================================
# QUICKSTART
# CLI-Encode:  python3 videobatch_extra.py --img 1.jpg 2.jpg --aud 1.mp3 2.mp3 --out outdir
# Selftests:   python3 videobatch_extra.py --selftest
# Edit:        micro videobatch_extra.py
# =========================================

# videobatch_extra.py
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path
from typing import List

from utils import build_out_name, human_time, validate_pair
from api import build_ffmpeg_cmd, run_ffmpeg


def cli_encode(
    images: List[Path],
    audios: List[Path],
    out_dir: Path,
    width: int = 1920,
    height: int = 1080,
    crf: int = 23,
    preset: str = "ultrafast",
    abitrate: str = "192k",
) -> int:
    """Encode multiple image/audio pairs into videos (CLI helper).

    Returns 0 on success, 1 if lists mismatch, or 2 when ffmpeg fails.
    """

    out_dir.mkdir(parents=True, exist_ok=True)
    if len(images) != len(audios):
        print("Fehler: Anzahl Bilder != Anzahl Audios")
        return 1
    total = len(images)
    done = 0
    errors = 0
    for i, (img, aud) in enumerate(zip(images, audios), 1):
        ok, msg = validate_pair(img, aud)
        if not ok:
            print(f"[{i}/{total}] {msg}: {img} / {aud}")
            errors += 1
            continue
        out_file = build_out_name(aud, out_dir)
        cmd = build_ffmpeg_cmd(
            str(img),
            str(aud),
            str(out_file),
            width,
            height,
            abitrate,
            crf,
            preset,
        )
        try:
            run_ffmpeg(cmd)
            done += 1
        except RuntimeError as e:
            print(f"FFmpeg-Fehler: {e}")
            errors += 1
    print(f"Fertig: {done}/{total}")
    return 0 if errors == 0 else 2


def run_selftests() -> int:
    """Run simple self-tests for CLI helpers."""

    assert human_time(65) == "01:05"
    with tempfile.TemporaryDirectory() as td:
        out = build_out_name(Path(td) / "a.mp3", Path(td))
        assert out.name.endswith(".mp4")
        assert re.search(r"a_\d{8}-\d{6}\.mp4$", out.name)
    print("Selftests OK")
    return 0


def main() -> None:
    """Command line interface entry point."""

    import argparse

    p = argparse.ArgumentParser(description="VideoBatchTool CLI / Tests")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--img", nargs="+")
    p.add_argument("--aud", nargs="+")
    p.add_argument("--out", default=".")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--crf", type=int, default=23)
    p.add_argument("--preset", default="ultrafast")
    p.add_argument("--abitrate", default="192k")
    args = p.parse_args()

    if args.selftest:
        sys.exit(run_selftests())
    if args.img and args.aud:
        images = [Path(p) for p in args.img]
        audios = [Path(p) for p in args.aud]
        out_dir = Path(args.out)
        sys.exit(
            cli_encode(
                images,
                audios,
                out_dir,
                args.width,
                args.height,
                args.crf,
                args.preset,
                args.abitrate,
            )
        )
    print("GUI starten: python3 videobatch_launcher.py")


if __name__ == "__main__":
    main()
