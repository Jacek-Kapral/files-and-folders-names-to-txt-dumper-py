"""
Przechodzi rekurencyjnie po folderze i zapisuje wszystkie katalogi oraz pliki
do pliku TXT w formie płaskiej listy ścieżek (jedna linia = jedna ścieżka).
Interaktywne menu: nazwa pliku wyjściowego, ścieżka docelowa, poziom zagnieżdżenia.

Użycie:
    python ffn2txt.py
"""

from pathlib import Path


def _collect_paths(
    root: Path, base: Path, current_depth: int, max_depth: int
) -> list[str]:
    """
    Zbiera ścieżki względne katalogów i plików pod base (względem root).
    max_depth=0: tylko zawartość roota; 1: + pierwsza warstwa podkatalogów; itd.
    """
    paths: list[str] = []
    try:
        items = sorted(base.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return paths
    for item in items:
        rel = item.relative_to(root)
        paths.append(str(rel).replace("\\", "/"))
        if item.is_dir() and current_depth < max_depth:
            paths.extend(
                _collect_paths(root, item, current_depth + 1, max_depth)
            )
    return paths


def write_tree_to_txt(
    source_dir: Path, output_path: Path, max_depth: int
) -> None:
    """
    Zapisuje drzewo katalogów i plików do pliku TXT (płaska lista ścieżek).

    @param source_dir Ścieżka do katalogu źródłowego
    @param output_path Ścieżka do pliku wynikowego .txt
    @param max_depth Poziom zagnieżdżenia (0=tylko root, 1=+1 warstwa, 2=+2 warstwy, …)
    """
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Nie jest katalogiem: {source_dir}")

    paths = ["."] + _collect_paths(source_dir, source_dir, 0, max_depth)
    output_path = output_path.resolve()
    output_path.write_text("\n".join(paths), encoding="utf-8")


def _script_dir() -> Path:
    """Katalog, w którym znajduje się skrypt."""
    return Path(__file__).resolve().parent


def _run_interactive_menu() -> None:
    """Prowadzi użytkownika przez pytania i uruchamia zapis drzewa."""
    print("--- Plik wyjściowy ---")
    output_name = input("Nazwa pliku wyjściowego [tree.txt]: ").strip() or "tree.txt"
    if not output_name.endswith(".txt"):
        output_name += ".txt"

    print("\n--- Ścieżka docelowa ---")
    target = input(
        "Ścieżka katalogu do przeszukania (pusta = katalog skryptu): "
    ).strip()
    source_dir = Path(target).resolve() if target else _script_dir()

    print("\n--- Poziom zagnieżdżenia ---")
    print("0 = tylko root, 1 = root + 1 warstwa podkatalogów, 2 = +2 warstwy, …")
    depth_input = input("Poziom zagnieżdżenia [0]: ").strip() or "0"
    try:
        max_depth = int(depth_input)
    except ValueError:
        max_depth = 0
    if max_depth < 0:
        max_depth = 0

    output_path = source_dir / output_name
    write_tree_to_txt(source_dir, output_path, max_depth)
    print(f"\nZapisano: {output_path}")


def main() -> None:
    _run_interactive_menu()


if __name__ == "__main__":
    main()
