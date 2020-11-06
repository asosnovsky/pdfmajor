#!/usr/bin/env python

"""
Converts AFM Files into jsons
"""
import argparse
import sys
import json

import warnings
import re
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from pathlib import Path

charcode_regex = re.compile(r"C\s+(\d+|-1)")
width_regex = re.compile(r"WX\s+(\d+)")
start_regex = re.compile(r"StartCharMetrics\s+(\d+)")
end_regex = re.compile(r"EndCharMetrics")


class AFMParserWarn(Warning):
    pass


class AFMCMIgnored(AFMParserWarn):
    pass


class CharMetric(NamedTuple):
    """
    A simple char-metric representation as defined in Adobe's AFM spec
    https://partners.adobe.com/public/developer/en/font/5004.AFM_Spec.pdf
    """

    char_code: int
    width: int

    @classmethod
    def from_line(cls, line: str):
        """takes a line from an afm file and parses out the values

        Args:
            line (str)

        Returns:
            CharMetric
        """
        char_code: int = -1
        width: int = 600
        charcode_match = charcode_regex.search(line, 0)
        if charcode_match is not None:
            char_code = int(charcode_match.groups()[0])
        width_match = width_regex.search(line, 0)
        if width_match is not None:
            width = int(width_match.groups()[0])
        return cls(char_code, width)


class SplitFile(NamedTuple):
    descriptor_raw: str
    metrics_raw: str


def split_file(data: str) -> SplitFile:
    start_match = start_regex.search(data, 0)
    if not start_match:
        raise AssertionError(f"Invalid AFM File no {start_regex} found")

    end_match = end_regex.search(data, 0)

    if not end_match:
        raise AssertionError(f"Invalid AFM File no {end_regex} found")

    return SplitFile(
        descriptor_raw=data[: start_match.start(0)].strip(),
        metrics_raw=data[start_match.end(0) : end_match.start(0)].strip(),
    )


def parse_descriptor(descriptor_raw: str) -> Dict[str, Any]:
    descriptor: Dict[str, Any] = {}
    for line in descriptor_raw.split("\n"):
        s_line = line.strip().split(" ")
        if len(s_line) < 2:
            warnings.warn(f"Ignoring descriptor line {line}", category=AFMCMIgnored)
        else:
            value: Any = ""
            key, *values = s_line
            if len(values) > 1:
                try:
                    value = list(map(int, values))
                except ValueError:
                    try:
                        value = list(map(float, values))
                    except ValueError:
                        value = " ".join([v.strip() for v in values])
            else:
                value = values[0].strip()
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
            descriptor[key.strip()] = value

    return descriptor


class ParsedFile(NamedTuple):
    descriptor: Dict[str, Any]
    metrics: List[CharMetric]

    @classmethod
    def from_data(cls, data: str):
        """parse afm text into ParsedFile

        Args:
            data (str)

        Raises:
            AssertionError

        Returns:
            ParsedFile
        """
        split_f = split_file(data)
        descriptor: Dict[str, str] = parse_descriptor(split_f.descriptor_raw)
        metrics = [
            CharMetric.from_line(line.strip())
            for line in split_f.metrics_raw.split("\n")
        ]
        return cls(descriptor=descriptor, metrics=metrics)

    @classmethod
    def from_file_path(cls, fpath: Path):
        data = fpath.read_text("ascii")
        return cls.from_data(data)

    def to_json(self):
        return {
            "descriptor": self.descriptor,
            "metrics": {
                "codes": [m.char_code for m in self.metrics],
                "widths": [m.width for m in self.metrics],
            },
        }


def make_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument(
        "files", type=Path, default=None, nargs="+", help="Files to process."
    )
    parser.add_argument(
        "-o", "--output-dir", default=None, help="Output directory for jsons", type=Path
    )
    return parser


# main
def main(args=None) -> int:

    argparser = make_argparser()
    parsed_args = argparser.parse_args(args=args)
    files = parsed_args.files  # type: List[Path]
    output_dir = parsed_args.output_dir  # type: Optional[Path]

    if output_dir is None:
        output_dir = Path("./")
        warnings.warn(
            f"No specified output folder using {output_dir.absolute()} for output",
            category=AFMParserWarn,
        )

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    errored: List[Tuple[Path, Exception]] = []
    for f in files:
        if f.suffix.lower() != ".afm":
            warnings.warn(f"Ignoring invalid file {f}", category=AFMParserWarn)
        out_path = output_dir / (f.stem + ".json")
        try:
            out_path.write_text(json.dumps(ParsedFile.from_file_path(f).to_json()))
        except Exception as e:
            errored.append((f, e))

    if len(errored) > 0:
        for fname, err in errored:
            warnings.warn(
                f"Failed to parse {fname} due to {err}", category=AFMParserWarn
            )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
