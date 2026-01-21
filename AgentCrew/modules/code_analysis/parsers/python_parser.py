"""
Python language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class PythonParser(BaseLanguageParser):
    """Parser for Python source code."""

    @property
    def language_name(self) -> str:
        return "python"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in ["class_definition", "function_definition"]:
            for child in node.children:
                if child.type == "identifier":
                    result["name"] = self.extract_node_text(child, source_code)
                elif child.type == "parameters":
                    params = []
                    for param in child.children:
                        if "parameter" in param.type or param.type == "identifier":
                            params.append(self.extract_node_text(param, source_code))
                    if params:
                        result["parameters"] = params

        elif node.type == "assignment":
            for child in node.children:
                if child.type == "identifier":
                    result["type"] = "variable_declaration"
                    result["name"] = self.extract_node_text(child, source_code)
                    return result
                break

        children = []
        for child in node.children:
            child_result = process_children_callback(child)
            if child_result and self._is_significant_node(child_result):
                children.append(child_result)

        if children:
            result["children"] = children

        return result
