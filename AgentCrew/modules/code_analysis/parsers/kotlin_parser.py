"""
Kotlin language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class KotlinParser(BaseLanguageParser):
    """Parser for Kotlin source code."""

    @property
    def language_name(self) -> str:
        return "kotlin"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in ["class_declaration", "function_declaration"]:
            for child in node.children:
                if child.type == "simple_identifier":
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
            return result

        elif node.type in ["property_declaration", "variable_declaration"]:
            for child in node.children:
                if child.type == "simple_identifier":
                    result["type"] = "variable_declaration"
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
                break
            return result

        children = []
        for child in node.children:
            child_result = process_children_callback(child)
            if child_result and self._is_significant_node(child_result):
                children.append(child_result)

        if children:
            result["children"] = children

        return result
