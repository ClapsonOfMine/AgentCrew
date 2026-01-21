"""
PHP language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class PhpParser(BaseLanguageParser):
    """Parser for PHP source code."""

    @property
    def language_name(self) -> str:
        return "php"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in [
            "class_declaration",
            "method_declaration",
            "function_definition",
            "interface_declaration",
            "trait_declaration",
        ]:
            for child in node.children:
                if child.type == "name":
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
            return result

        elif node.type in ["property_declaration", "const_declaration"]:
            for child in node.children:
                if child.type in ["property_element", "const_element"]:
                    for subchild in child.children:
                        if subchild.type in ["variable_name", "name"]:
                            result["type"] = "variable_declaration"
                            result["name"] = self.extract_node_text(
                                subchild, source_code
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
