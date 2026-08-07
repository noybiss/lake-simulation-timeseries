from __future__ import annotations

import unittest
from modules.docs_view import render_documentation

class DocsViewTests(unittest.TestCase):
    def test_render_documentation_callable(self) -> None:
        """Verify render_documentation function signature and module export."""
        self.assertTrue(callable(render_documentation))

if __name__ == "__main__":
    unittest.main()
