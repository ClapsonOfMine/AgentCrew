"""
C++ language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class CppParser(BaseLanguageParser):
    """Parser for C++ source code."""

    @property
    def language_name(self) -> str:
        return "cpp"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in ["class_specifier", "function_definition", "struct_specifier"]:
            for child in node.children:
                if child.type == "identifier":
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
            return result

        elif node.type in ["declaration", "variable_declaration"]:
            for child in node.children:
                if child.type in ["init_declarator", "declarator"]:
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            result["type"] = "variable_declaration"
                            result["name"] = self.extract_node_text(
                                subchild, source_code
                            )
                            return result
            return result

        children = []
        for child in node.children:
            child_result = process_children_callback(child)
            if child_result and self._is_significant_node(child_result):
                children.append(child_result)

        if children:
            result["children"] = children

        return result
