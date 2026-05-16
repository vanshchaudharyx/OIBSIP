#!/usr/bin/env python3
"""
CLI Password Generator — Beginner-friendly command-line tool.

Usage:
    python cli.py
    python cli.py --length 20 --no-symbols
    python cli.py --length 12 --only-digits
"""
import argparse
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import PasswordGenerator, PasswordConfig
from utils.validators import validate_length, validate_char_types

# ── ANSI colours ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

STRENGTH_COLORS = {
    0: RED,
    1: "\033[33m",   # orange-ish
    2: YELLOW,
    3: GREEN,
    4: "\033[92m",   # bright green
}

BANNER = f"""
{CYAN}{BOLD}╔══════════════════════════════════════╗
║   🔐  Secure Password Generator     ║
╚══════════════════════════════════════╝{RESET}
"""


def print_banner():
    print(BANNER)


def interactive_mode():
    """Step-by-step interactive wizard."""
    print_banner()
    print(f"{GRAY}No arguments supplied — entering interactive mode.{RESET}\n")

    # Length
    while True:
        raw = input(f"{WHITE}Password length {GRAY}(default 16): {RESET}").strip() or "16"
        ok, err, length = validate_length(raw)
        if ok:
            break
        print(f"{RED}✗ {err}{RESET}")

    # Character types
    print()
    def ask_bool(prompt, default=True) -> bool:
        default_str = "Y/n" if default else "y/N"
        ans = input(f"{WHITE}{prompt} {GRAY}[{default_str}]: {RESET}").strip().lower()
        if ans == "":
            return default
        return ans in ("y", "yes", "1", "true")

    use_upper   = ask_bool("Include UPPERCASE letters?")
    use_lower   = ask_bool("Include lowercase letters?")
    use_digits  = ask_bool("Include digits (0-9)?")
    use_symbols = ask_bool("Include symbols (!@#...)?")

    ok, err = validate_char_types(use_upper, use_lower, use_digits, use_symbols)
    if not ok:
        print(f"{RED}✗ {err}{RESET}")
        sys.exit(1)

    # Extras
    print()
    exclude_ambiguous = ask_bool("Exclude ambiguous chars (l, 1, O, 0, I)?", default=False)
    raw_excl = input(f"{WHITE}Characters to exclude {GRAY}(leave blank for none): {RESET}").strip()

    # Count
    while True:
        raw_count = input(f"\n{WHITE}How many passwords to generate? {GRAY}(default 1): {RESET}").strip() or "1"
        try:
            count = int(raw_count)
            if 1 <= count <= 50:
                break
            print(f"{RED}✗ Enter a number between 1 and 50.{RESET}")
        except ValueError:
            print(f"{RED}✗ Enter a valid number.{RESET}")

    config = PasswordConfig(
        length=length,
        use_uppercase=use_upper,
        use_lowercase=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_chars=raw_excl,
        exclude_ambiguous=exclude_ambiguous,
    )

    generator = PasswordGenerator(config)
    passwords = generator.generate_batch(count)

    print(f"\n{CYAN}{BOLD}{'─'*42}{RESET}")
    print(f"{BOLD}  Generated Password{'s' if count > 1 else ''}{RESET}")
    print(f"{CYAN}{'─'*42}{RESET}\n")

    for i, pwd in enumerate(passwords, 1):
        score, label, color_hex, tip = PasswordGenerator.evaluate_strength(pwd)
        bar_color = STRENGTH_COLORS[score]
        bar = "█" * (score + 1) + "░" * (4 - score)
        prefix = f"  {GRAY}{i:>2}.{RESET} " if count > 1 else "  "
        print(f"{prefix}{BOLD}{WHITE}{pwd}{RESET}")
        print(f"       {bar_color}{bar}  {label}{RESET}  {GRAY}{tip}{RESET}\n")

    print(f"{CYAN}{'─'*42}{RESET}")
    print(f"{GRAY}  Tip: Run with --help for non-interactive usage.{RESET}\n")


def cli_mode(args):
    """Non-interactive CLI driven by argparse flags."""
    ok, err, length = validate_length(str(args.length))
    if not ok:
        print(f"{RED}Error: {err}{RESET}")
        sys.exit(1)

    ok, err = validate_char_types(
        not args.no_upper,
        not args.no_lower,
        not args.no_digits,
        not args.no_symbols,
    )
    if not ok:
        print(f"{RED}Error: {err}{RESET}")
        sys.exit(1)

    config = PasswordConfig(
        length=length,
        use_uppercase=not args.no_upper,
        use_lowercase=not args.no_lower,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
        exclude_chars=args.exclude or "",
        exclude_ambiguous=args.no_ambiguous,
    )

    generator = PasswordGenerator(config)
    passwords = generator.generate_batch(args.count)

    if args.quiet:
        for pwd in passwords:
            print(pwd)
    else:
        print_banner()
        for i, pwd in enumerate(passwords, 1):
            score, label, _, tip = PasswordGenerator.evaluate_strength(pwd)
            bar_color = STRENGTH_COLORS[score]
            bar = "█" * (score + 1) + "░" * (4 - score)
            prefix = f"{GRAY}{i:>2}. {RESET}" if args.count > 1 else ""
            print(f"  {prefix}{BOLD}{WHITE}{pwd}{RESET}  {bar_color}{bar} {label}{RESET}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="🔐 Secure Password Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                        # interactive wizard
  python cli.py --length 20            # 20-char password
  python cli.py --length 16 --count 5  # 5 passwords
  python cli.py --no-symbols           # letters + digits only
  python cli.py --length 32 --quiet    # bare output, no decorations
        """,
    )
    parser.add_argument("--length",       type=int, default=None, help="Password length (4–512)")
    parser.add_argument("--count",        type=int, default=1,    help="Number of passwords")
    parser.add_argument("--no-upper",     action="store_true",    help="Exclude uppercase letters")
    parser.add_argument("--no-lower",     action="store_true",    help="Exclude lowercase letters")
    parser.add_argument("--no-digits",    action="store_true",    help="Exclude digits")
    parser.add_argument("--no-symbols",   action="store_true",    help="Exclude symbols")
    parser.add_argument("--no-ambiguous", action="store_true",    help="Exclude ambiguous chars (l,1,O,0,I)")
    parser.add_argument("--exclude",      type=str, default="",   help="Specific chars to exclude")
    parser.add_argument("--quiet",        action="store_true",    help="Output passwords only (no decoration)")

    args = parser.parse_args()

    if args.length is None and len(sys.argv) == 1:
        # No arguments at all → interactive
        interactive_mode()
    else:
        # At least one flag provided → CLI mode with defaults
        if args.length is None:
            args.length = 16
        cli_mode(args)


if __name__ == "__main__":
    main()