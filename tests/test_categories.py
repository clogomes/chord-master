import unittest
import ast
from core.categories import CATEGORY_ROUTES

class TestCategoryRoutes(unittest.TestCase):
    def test_routes_are_valid_in_app(self):
        with open("gui/app.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        valid_routes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "navigate_to":
                for child in ast.walk(node):
                    if isinstance(child, ast.Compare):
                        for op, comp in zip(child.ops, child.comparators):
                            if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant):
                                if isinstance(comp.value, str):
                                    valid_routes.add(comp.value)
        
        # Add main_menu as a fallback just in case
        valid_routes.add("main_menu")

        for cat, route in CATEGORY_ROUTES.items():
            self.assertIn(route, valid_routes, f"Rota '{route}' para '{cat}' não é válida no navigate_to")
