"""Command-line interface.

    emg-bids init <dataset_dir> --name <name> [--author <name>]... [--license <license>]
    emg-bids add <dataset_dir> <recording_file> --subject <label> --task <label> --emg-reference <text> [...]
"""

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from .core.schema import load
from .models.dataset_description import DatasetDescription
from .models.emg.entities import Entities
from .readers import READERS, read
from .writers.dataset import add_recording, init_dataset

_PACKAGE = "emg-bids-converter"
_CODE_URL = "https://github.com/hugohaffad/emg_bids_converter"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="emg-bids", description="Convert EMG recordings to an EMG-BIDS dataset.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {version(_PACKAGE)}")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create an empty BIDS dataset")
    init.add_argument("root", type=Path, help="dataset directory to create (must not exist or be empty)")
    init.add_argument("--name", required=True, help="dataset_description.json Name")
    init.add_argument("--author", action="append", dest="authors", metavar="NAME",
                      help="dataset_description.json Authors; repeat for each author")
    init.add_argument("--license", help="dataset_description.json License, e.g. CC-BY-4.0")

    add = commands.add_parser("add", help="add one recording to a dataset created with init")
    add.add_argument("root", type=Path, help="dataset directory")
    add.add_argument("file", type=Path, help=f"recording file ({', '.join(sorted(READERS))})")
    add.add_argument("--subject", required=True, help="sub-<label>")
    add.add_argument("--task", required=True, help="task-<label>")
    add.add_argument("--session", help="ses-<label>")
    add.add_argument("--acquisition", help="acq-<label>")
    add.add_argument("--run", help="run-<index>")
    add.add_argument("--recording", help="recording-<label>")
    add.add_argument("--emg-reference", required=True, help="*_emg.json EMGReference")
    add.add_argument("--powerline-frequency", type=float, default=50.0,
                     help="*_emg.json PowerLineFrequency in Hz (default: 50)")
    return parser


def _init(args: argparse.Namespace) -> None:
    description = DatasetDescription(
        Name=args.name,
        BIDSVersion=load()["bids_version"],
        Authors=args.authors,
        License=args.license,
        GeneratedBy=[{"Name": _PACKAGE, "Version": version(_PACKAGE), "CodeURL": _CODE_URL}],
    )
    init_dataset(args.root, description)
    print(f"Created dataset {args.name!r} in {args.root}")


def _add(args: argparse.Namespace) -> None:
    entities = Entities(
        subject=args.subject,
        task=args.task,
        session=args.session,
        acquisition=args.acquisition,
        run=args.run,
        recording=args.recording,
    )
    recording = read(
        args.file,
        task_name=args.task,
        emg_reference=args.emg_reference,
        powerline_frequency=args.powerline_frequency,
    )
    written = add_recording(args.root, entities, recording)
    print(f"Added {args.file.name} as sub-{args.subject} ({len(written)} files written)")


def main(argv: list[str] | None = None) -> int:
    """Entry point of the emg-bids command; returns the process exit code"""
    args = _parser().parse_args(argv)
    commands = {"init": _init, "add": _add}
    try:
        commands[args.command](args)
    except (OSError, ValueError, TypeError) as error:
        # Expected failures (invalid BIDS value, missing file, existing recording): a message, not a traceback
        print(f"emg-bids: error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
