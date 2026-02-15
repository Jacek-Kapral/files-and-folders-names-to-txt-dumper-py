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


def get_tree_paths(source_dir: Path, max_depth: int) -> list[str]:
    """
    Zbiera listę ścieżek drzewa (dry run lub przed zapisem).

    @param source_dir Ścieżka do katalogu źródłowego
    @param max_depth Poziom zagnieżdżenia (0=tylko root, 1=+1 warstwa, …)
    @returns Lista ścieżek względnych z kropką na początku
    """
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Nie jest katalogiem: {source_dir}")
    return ["."] + _collect_paths(source_dir, source_dir, 0, max_depth)


def write_paths_to_file(paths: list[str], output_path: Path) -> None:
    """
    Zapisuje listę ścieżek do pliku TXT.

    @param paths Lista ścieżek (jedna na linię)
    @param output_path Ścieżka do pliku wynikowego
    """
    output_path = output_path.resolve()
    output_path.write_text("\n".join(paths), encoding="utf-8")


def _script_dir() -> Path:
    """Katalog, w którym znajduje się skrypt."""
    return Path(__file__).resolve().parent


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Pyta użytkownika tak/nie. Zwraca True dla y/yes, False dla n/no."""
    suffix = " [T/n]: " if default else " [t/N]: "
    raw = input(prompt + suffix).strip().lower()
    if not raw:
        return default
    return raw in ("t", "y", "tak", "yes")


def _resolve_output_path(output_name: str, source_dir: Path) -> Path:
    """Ścieżka pełna, jeśli podana; w przeciwnym razie katalog źródłowy + nazwa."""
    p = Path(output_name)
    if p.is_absolute() or "/" in output_name or "\\" in output_name:
        return p.resolve()
    return source_dir / output_name


def _run_interactive_menu() -> None:
    """Prowadzi użytkownika przez pytania, dry run i ewentualny zapis drzewa."""
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

    print("\n--- Dry run (skanowanie) ---")
    paths = get_tree_paths(source_dir, max_depth)
    count = len(paths)

    if count > 1000:
        print(
            f"Znaleziono {count} obiektów (folderów i plików). "
            "Przetworzenie może potrwać."
        )
        if not _ask_yes_no("Kontynuować?", default=True):
            print("Przerwano.")
            return
    else:
        print(f"Dry run zakończony pomyślnie. Znaleziono {count} obiektów. Gotowy do zapisania.")

    if not _ask_yes_no("Zapisać plik?", default=True):
        print("Nie zapisano.")
        return

    output_path = _resolve_output_path(output_name, source_dir)
    write_paths_to_file(paths, output_path)
    print(f"Zapisano: {output_path}")


def main() -> None:
    _run_interactive_menu()


if __name__ == "__main__":
    main()
