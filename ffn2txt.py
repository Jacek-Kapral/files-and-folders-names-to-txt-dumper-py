"""
Przechodzi rekurencyjnie po folderze i zapisuje wszystkie katalogi oraz pliki
do pliku TXT w formie płaskiej listy ścieżek (jedna linia = jedna ścieżka).

Użycie:
    python ffn2txt.py [folder] [-o plik_wyjściowy.txt]
"""

import argparse
from pathlib import Path


def _collect_paths(root: Path, base: Path) -> list[str]:
    """Zbiera ścieżki względne katalogów i plików pod base (względem root)."""
    paths: list[str] = []
    try:
        items = sorted(base.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return paths
    for item in items:
        rel = item.relative_to(root)
        paths.append(str(rel).replace("\\", "/"))
        if item.is_dir():
            paths.extend(_collect_paths(root, item))
    return paths


def write_tree_to_txt(source_dir: Path, output_path: Path) -> None:
    """
    Zapisuje drzewo katalogów i plików do pliku TXT (płaska lista ścieżek).

    @param source_dir Ścieżka do katalogu źródłowego
    @param output_path Ścieżka do pliku wynikowego .txt
    """
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Nie jest katalogiem: {source_dir}")

    paths = ["."] + _collect_paths(source_dir, source_dir)
    output_path = output_path.resolve()
    output_path.write_text("\n".join(paths), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Zapisuje drzewo plików i folderów do pliku TXT (płaska lista)."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        type=Path,
        help="Katalog startowy (domyślnie: bieżący)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("tree.txt"),
        help="Plik wyjściowy TXT (domyślnie: tree.txt)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    write_tree_to_txt(args.folder, args.output)


if __name__ == "__main__":
    main()
