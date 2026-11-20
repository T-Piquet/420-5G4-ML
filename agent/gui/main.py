import argparse
from pathlib import Path
from .app import App

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(Path(__file__).resolve().parent.parent / "data"))
    arg = parser.parse_args()
    App(Path(arg.data_dir)).mainloop()

if __name__ == "__main__":
    main()