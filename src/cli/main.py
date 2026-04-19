import argparse
import sys
import logging
from src.converter.chirp import ChirpParser, ChirpGenerator
from src.converter.btech import BtechParser, BtechGenerator
from src.converter.clipboard import ClipboardParser, ClipboardGenerator

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Chirp2UVPro CLI tool for radio frequency configuration conversion."
    )
    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    # 'convert' subcommand
    convert_parser = subparsers.add_parser('convert', help='Convert configuration between formats')
    convert_parser.add_argument(
        '--from', 
        dest='from_format', 
        required=True, 
        choices=['chirp', 'btech', 'clipboard'], 
        help='Source format'
    )
    convert_parser.add_argument(
        '--to', 
        dest='to_format', 
        required=True, 
        choices=['chirp', 'btech', 'clipboard'], 
        help='Target format'
    )
    convert_parser.add_argument(
        '--input', 
        type=argparse.FileType('r'), 
        default=sys.stdin, 
        help='Input file (defaults to stdin)'
    )
    convert_parser.add_argument(
        '--output', 
        type=argparse.FileType('w'), 
        default=sys.stdout, 
        help='Output file (defaults to stdout)'
    )
    
    # Additional argument for clipboard format (json or csv)
    convert_parser.add_argument(
        '--clipboard-format', 
        choices=['json', 'csv'], 
        default='json', 
        help='Format for clipboard output (default: json)'
    )

    args = parser.parse_args()

    if args.command == 'convert':
        try:
            # 1. Read input
            input_content = args.input.read()

            # 2. Parse input
            channels = []
            if args.from_format == 'chirp':
                parser_obj = ChirpParser()
            elif args.from_format == 'btech':
                parser_obj = BtechParser()
            elif args.from_format == 'clipboard':
                parser_obj = ClipboardParser()
            else:
                # This part should technically be unreachable due to argparse choices
                logger.error(f"Unsupported from_format: {args.from_format}")
                sys.exit(1)

            channels = parser_obj.parse(input_content)

            if not channels:
                logger.warning("No channels found in input.")
                if args.output is not sys.stdout:
                    args.output.write("")
                return

            # 3. Generate output
            if args.to_format == 'chirp':
                generator = ChirpGenerator()
            elif args.to_format == 'btech':
                generator = BtechGenerator()
            elif args.to_format == 'clipboard':
                generator = ClipboardGenerator(format=args.clipboard_format)
            else:
                # This part should technically be unreachable due to argparse choices
                logger.error(f"Unsupported to_format: {args.to_format}")
                sys.exit(1)

            output_content = generator.generate(channels)

            # 4. Write output
            args.output.write(output_content)
            # Add a newline if we are writing to a file to ensure it ends with one, 
            # but be careful with stdout if it's being piped.
            # Actually, stdout usually expects the caller to handle newlines, 
            # but for files it's cleaner. 
            # Let's stick to what the generator provides.
            if args.output is not sys.stdout:
                args.output.write('\n')

        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
