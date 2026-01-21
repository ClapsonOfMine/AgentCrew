"""
Rust language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class RustParser(BaseLanguageParser):
    """Parser for Rust source code."""

    @property
    def language_name(self) -> str:
        return "rust"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in ["struct_item", "impl_item", "fn_item", "trait_item"]:
            for child in node.children:
                if child.type == "identifier":
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
            return result

        elif node.type in ["static_item", "const_item", "let_declaration"]:
            for child in node.children:
                if child.type == "identifier":
                    result["type"] = "variable_declaration"
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
                elif child.type == "pattern" and child.children:
                    result["name"] = self.extract_node_text(
                        child.children[0], source_code
                    )
            return result

        children = []
        for child in node.children:
            child_result = process_children_callback(child)
            if child_result and self._is_significant_node(child_result):
                children.append(child_result)

        if children:
            result["children"] = children

        return result
