import argparse

from kakaw.models.constants import DAYS, minutes_to_hhmm
from kakaw.problems import Problem
from kakaw.utils.parser import Parser


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a student-course timetable.",
        epilog="""examples:
  # Run Steepest Ascent Hill-Climbing
  uv run kakaw --test tests/sample.json --algorithm steepest-hc --plot output.png

  # Run Simulated Annealing
  uv run kakaw --test tests/sample.json --algorithm simulated --plot output.png

  # Run Genetic Algorithm
  uv run kakaw --test tests/sample.json --algorithm genetic --plot output.png""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-t", "--test", required=True, help="path to test file")

    parser.add_argument(
        "-a",
        "--algorithm",
        required=True,
        choices=["simple-hc", "steepest-hc", "simulated", "genetic"],
        help="algorithm to use",
    )

    parser.add_argument("-p", "--plot", help="path to output plot")

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show detailed output"
    )

    return parser


def main() -> None:
    args = create_parser().parse_args()

    instance = Parser(args.test).parse()
    problem = Problem(instance)

    if args.verbose:
      pass
      
    if args.plot:
      pass
