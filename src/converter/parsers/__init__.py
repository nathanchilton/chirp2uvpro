from ..base import BaseParser
from ..chirp import ChirpParser, ChirpGenerator
from ..btech import BtechParser, BtechGenerator
from ..clipboard import ClipboardParser, ClipboardGenerator
from .api_import import ApiImportParser

class ParserFactory:
    @staticmethod
    def get_parser(fmt: str) -> BaseParser:
        if fmt == 'chirp':
            return ChirpParser()
        elif fmt == 'btech':
            return BtechParser()
        elif fmt == 'clipboard':
            return ClipboardParser()
        elif fmt == 'api-import':
            return ApiImportParser()
        else:
            # Default to Btech if unknown
            return BtechParser()
