
import unittest
from src.converter.clipboard import ClipboardParser

class TestClipboardParserIdentification(unittest.TestCase):
    def setUp(self):
        self.parser = ClipboardParser()

    def test_misidentification_as_json(self):
        # This is a random JSON that is NOT a clipboard format
        content = '{"random": "data"}'
        channels = self.parser.parse(content)
        # It should probably NOT identify this as a valid clipboard format if it doesn't have the prefix
        # Currently, it will probably identify it because it finds '{'
        self.assertEqual(len(channels), 0)

if __name__ == '__main__':
    unittest.main()
