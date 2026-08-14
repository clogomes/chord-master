"""Unit tests for gui/markdown_renderer.py — parsing and rendering logic."""
import unittest
from gui.markdown_renderer import (
    parse_markdown_line_type,
    is_table_delimiter,
    parse_table_cells,
    parse_inline_bold,
)


class TestMarkdownLineClassifier(unittest.TestCase):
    """Tests for parse_markdown_line_type()."""

    def test_empty_line(self):
        self.assertEqual(parse_markdown_line_type(""), "empty")
        self.assertEqual(parse_markdown_line_type("   "), "empty")

    def test_h1(self):
        self.assertEqual(parse_markdown_line_type("# Título Principal"), "h1")

    def test_h2(self):
        self.assertEqual(parse_markdown_line_type("## Sub-título"), "h2")

    def test_h3(self):
        self.assertEqual(parse_markdown_line_type("### Secção 3"), "h3")

    def test_separator(self):
        self.assertEqual(parse_markdown_line_type("---"), "separator")
        self.assertEqual(parse_markdown_line_type("***"), "separator")

    def test_bullet_dot(self):
        self.assertEqual(parse_markdown_line_type("• Nota importante"), "bullet")

    def test_bullet_dash(self):
        self.assertEqual(parse_markdown_line_type("- Item da lista"), "bullet")

    def test_bullet_asterisk(self):
        self.assertEqual(parse_markdown_line_type("* Item com asterisco"), "bullet")

    def test_table_row(self):
        self.assertEqual(parse_markdown_line_type("| Coluna 1 | Coluna 2 |"), "table_row")

    def test_table_delimiter(self):
        self.assertEqual(parse_markdown_line_type("| :--- | :--- |"), "table_delimiter")

    def test_paragraph(self):
        self.assertEqual(parse_markdown_line_type("Um parágrafo simples."), "paragraph")
        self.assertEqual(parse_markdown_line_type("Texto com **negrito** inline."), "paragraph")


class TestTableDelimiterDetection(unittest.TestCase):
    """Tests for is_table_delimiter()."""

    def test_recognises_alignment_row(self):
        self.assertTrue(is_table_delimiter("| :--- | :--- | :--- |"))
        self.assertTrue(is_table_delimiter("| --- | --- |"))
        self.assertTrue(is_table_delimiter("| :---: | ---: | :--- |"))

    def test_rejects_data_row(self):
        self.assertFalse(is_table_delimiter("| Dó | C | 261 Hz |"))
        self.assertFalse(is_table_delimiter("| :--- | texto aqui |"))

    def test_rejects_non_table_lines(self):
        self.assertFalse(is_table_delimiter("---"))
        self.assertFalse(is_table_delimiter("texto simples"))


class TestParseTableCells(unittest.TestCase):
    """Tests for parse_table_cells()."""

    def test_basic_three_column_row(self):
        cells = parse_table_cells("| Uníssono | P1 | Perfeito |")
        self.assertEqual(cells, ["Uníssono", "P1", "Perfeito"])

    def test_strips_whitespace(self):
        cells = parse_table_cells("|  a  |  b  |  c  |")
        self.assertEqual(cells, ["a", "b", "c"])

    def test_single_column(self):
        cells = parse_table_cells("| Apenas uma célula |")
        self.assertEqual(cells, ["Apenas uma célula"])

    def test_bold_preserved(self):
        cells = parse_table_cells("| **Negrito** | Simples |")
        self.assertEqual(cells, ["**Negrito**", "Simples"])


class TestParseInlineBold(unittest.TestCase):
    """Tests for parse_inline_bold()."""

    def test_no_bold(self):
        result = parse_inline_bold("Texto normal sem negrito.")
        self.assertEqual(result, [("Texto normal sem negrito.", False)])

    def test_fully_bold(self):
        result = parse_inline_bold("**Totalmente negrito**")
        self.assertEqual(result, [("Totalmente negrito", True)])

    def test_mixed_inline(self):
        result = parse_inline_bold("Começo **negrito** e fim.")
        self.assertEqual(result, [("Começo ", False), ("negrito", True), (" e fim.", False)])

    def test_multiple_bold_spans(self):
        result = parse_inline_bold("**A** e **B** no meio.")
        self.assertIn(("A", True), result)
        self.assertIn(("B", True), result)
        bold_chunks = [text for text, bold in result if bold]
        self.assertEqual(bold_chunks, ["A", "B"])

    def test_empty_string(self):
        result = parse_inline_bold("")
        self.assertEqual(result, [])

    def test_unclosed_bold_treated_as_plain(self):
        result = parse_inline_bold("Texto **incompleto")
        # No closing **, so treated as regular text
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0][1])


if __name__ == "__main__":
    unittest.main()
