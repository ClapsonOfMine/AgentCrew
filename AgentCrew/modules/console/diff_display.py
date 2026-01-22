"""
Diff display helper for showing file changes in console UI.
Provides split view diff display with syntax highlighting.
"""

import difflib
from typing import List, Dict
from rich.text import Text
from rich.table import Table
from rich.box import SIMPLE_HEAD
from .constants import (
    RICH_STYLE_BLUE_BOLD,
)


class DiffDisplay:
    """Helper class for creating split diff views."""

    @staticmethod
    def has_search_replace_blocks(blocks: List[Dict]) -> bool:
        """Check if input is a valid list of search/replace blocks."""
        if not isinstance(blocks, list):
            return False
        return len(blocks) > 0 and all(
            isinstance(b, dict) and "search" in b and "replace" in b for b in blocks
        )

    @staticmethod
    def parse_search_replace_blocks(blocks: List[Dict]) -> List[Dict]:
        """
        Parse search/replace blocks from list format.

        Args:
            blocks: List of dicts with 'search' and 'replace' keys

        Returns:
            List of dicts with 'index', 'search', and 'replace' keys
        """
        if not isinstance(blocks, list):
            return []

        return [
            {
                "index": i,
                "search": block.get("search", ""),
                "replace": block.get("replace", ""),
            }
            for i, block in enumerate(blocks)
            if isinstance(block, dict)
        ]

    @staticmethod
    def create_split_diff_table(
        original: str, modified: str, max_width: int = 60
    ) -> Table:
        """
        Create a split diff display table using difflib for intelligent comparison.

        Args:
            original: Original text content
            modified: Modified text content
            max_width: Maximum width for each column

        Returns:
            Rich Table object with split diff view
        """
        table = Table(
            show_header=True,
            header_style=RICH_STYLE_BLUE_BOLD,
            box=SIMPLE_HEAD,
            expand=False,
            padding=(0, 1),
        )
        table.add_column("Original", style="", width=max_width, no_wrap=False)
        table.add_column("Modified", style="", width=max_width, no_wrap=False)

        original_lines = original.split("\n")
        modified_lines = modified.split("\n")

        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    orig_text = Text(f"  {original_lines[i]}", style="dim")
                    mod_text = Text(f"  {modified_lines[j]}", style="dim")
                    table.add_row(orig_text, mod_text)

            elif tag == "delete":
                for i in range(i1, i2):
                    orig_text = Text(f"- {original_lines[i]}", style="red")
                    mod_text = Text("", style="dim")
                    table.add_row(orig_text, mod_text)

            elif tag == "insert":
                for j in range(j1, j2):
                    orig_text = Text("", style="dim")
                    mod_text = Text(f"+ {modified_lines[j]}", style="green")
                    table.add_row(orig_text, mod_text)

            elif tag == "replace":
                max_lines = max(i2 - i1, j2 - j1)

                for offset in range(max_lines):
                    orig_idx = i1 + offset
                    mod_idx = j1 + offset

                    if orig_idx < i2 and mod_idx < j2:
                        orig_line = original_lines[orig_idx]
                        mod_line = modified_lines[mod_idx]

                        char_matcher = difflib.SequenceMatcher(
                            None, orig_line, mod_line
                        )
                        if char_matcher.ratio() > 0.5:
                            orig_text = DiffDisplay._highlight_char_diff(
                                orig_line, mod_line, is_original=True
                            )
                            mod_text = DiffDisplay._highlight_char_diff(
                                orig_line, mod_line, is_original=False
                            )
                        else:
                            orig_text = Text(f"- {orig_line}", style="red")
                            mod_text = Text(f"+ {mod_line}", style="green")

                        table.add_row(orig_text, mod_text)

                    elif orig_idx < i2:
                        orig_text = Text(f"- {original_lines[orig_idx]}", style="red")
                        mod_text = Text("", style="dim")
                        table.add_row(orig_text, mod_text)

                    elif mod_idx < j2:
                        orig_text = Text("", style="dim")
                        mod_text = Text(f"+ {modified_lines[mod_idx]}", style="green")
                        table.add_row(orig_text, mod_text)

        return table

    @staticmethod
    def _highlight_char_diff(orig_line: str, mod_line: str, is_original: bool) -> Text:
        """
        Highlight character-level differences within a line.

        Args:
            orig_line: Original line text
            mod_line: Modified line text
            is_original: True to highlight original, False for modified

        Returns:
            Rich Text with character-level highlighting
        """
        result = Text()
        if is_original:
            result.append("- ", style="red")
        else:
            result.append("+ ", style="green")
        matcher = difflib.SequenceMatcher(None, orig_line, mod_line)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if is_original:
                segment = orig_line[i1:i2]
                if tag == "equal":
                    result.append(segment, style="dim")
                elif tag == "delete":
                    result.append(segment, style="red on #3d0000")
                elif tag == "replace":
                    result.append(segment, style="red on #3d0000")
            else:
                segment = mod_line[j1:j2]
                if tag == "equal":
                    result.append(segment, style="dim")
                elif tag == "insert":
                    result.append(segment, style="green on #003d00")
                elif tag == "replace":
                    result.append(segment, style="green on #003d00")

        return result
