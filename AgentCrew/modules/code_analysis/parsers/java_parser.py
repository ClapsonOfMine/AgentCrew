"""
Java language parser for code analysis.
"""

from typing import Any, Dict, Optional

from .base import BaseLanguageParser


class JavaParser(BaseLanguageParser):
    """Parser for Java source code."""

    @property
    def language_name(self) -> str:
        return "java"

    def process_node(
        self, node, source_code: bytes, process_children_callback
    ) -> Optional[Dict[str, Any]]:
        result = self._create_base_result(node)

        if node.type in ["class_declaration", "interface_declaration"]:
            for child in node.children:
                if child.type == "identifier":
                    result["name"] = self.extract_node_text(child, source_code)
                elif child.type in ["class_body", "interface_body"]:
                    result["children"] = [
                        process_children_callback(c) for c in child.children
                    ]

        elif node.type == "method_declaration":
            self._handle_method_declaration(node, source_code, result)

        elif node.type == "field_declaration":
            self._handle_field_declaration(node, source_code, result)

        elif node.type == "annotation":
            annotation_name = self.extract_node_text(node, source_code)
            result["name"] = annotation_name
            result["type"] = "annotation"

        elif node.type == "lambda_expression":
            result["type"] = "lambda_expression"

        children = [process_children_callback(child) for child in node.children]
        if children:
            result["children"] = children

        return result

    def _handle_method_declaration(
        self, node, source_code: bytes, result: Dict[str, Any]
    ) -> None:
        method_name = None
        parameters = []
        return_type = None

        for child in node.children:
            if child.type == "identifier":
                method_name = self.extract_node_text(child, source_code)
                result["name"] = method_name
            elif child.type == "formal_parameters":
                for param in child.children:
                    if param.type == "parameter":
                        param_name = self.extract_node_text(
                            param.child_by_field_name("name"), source_code
                        )
                        param_type = self.extract_node_text(
                            param.child_by_field_name("type"), source_code
                        )
                        parameters.append(f"{param_type} {param_name}")
                result["parameters"] = parameters
            elif child.type == "type":
                return_type = self.extract_node_text(child, source_code)
                result["return_type"] = return_type

    def _handle_field_declaration(
        self, node, source_code: bytes, result: Dict[str, Any]
    ) -> None:
        for child in node.children:
            if child.type == "variable_declarator":
                var_name = self.extract_node_text(
                    child.child_by_field_name("name"), source_code
                )
                var_type = self.extract_node_text(
                    child.child_by_field_name("type"), source_code
                )
                result["name"] = var_name
                result["variable_type"] = var_type
                result["type"] = "field_declaration"
