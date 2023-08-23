import unittest
import json

from .parser import parse_prerequisite_list, parse_prerequisites
from .prerequisites import ParsedPrerequisite, SingleClass, ClassGroup, Operator

# prerequisites = [['Math 120', 'or Math 124', 'or Math 128', 'or APBC', 'or OXMA'], ['and Phys 120', 'or Phys 125', 'or APPE']]
# prerequisites = ['Math 101', 'and Math 100', 'and Math 201']
# prerequisites = ["1", "and 2", "and 3", "or 4"]


class TestPrerequiteParsing(unittest.TestCase):
    def test_single_class(self):
        input = ["1"]

        expected = SingleClass("1")

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_simple(self):
        input = [
            "1",
            "and 2",
            "and 3",
        ]

        expected = ClassGroup(
            SingleClass("1"),
            SingleClass("2", prefixed_operator=Operator.And),
            SingleClass("3", prefixed_operator=Operator.And),
            op=Operator.And,
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_simple_group(self):
        input = [
            "( 1",
            "or 2",
            "or 3)",
        ]

        expected = ClassGroup(
            SingleClass("1"),
            SingleClass("2"),
            SingleClass("3"),
            op=Operator.Or,
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_simple_operator_precedence(self):
        input = [
            "1",
            "and 2",
            "or 3",
        ]

        expected = ClassGroup(
            ClassGroup(SingleClass("1"), SingleClass("2"), op=Operator.And),
            SingleClass("3"),
            op=Operator.Or,
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_machine_learning(self):
        input = [
            "COMP 229",
            "(and MATH 210",
            "and MATH 214",
            "or COMP 149)",
            "(and COMP 146",
            "or MATH 150)",
        ]

        expected = ClassGroup(
            SingleClass("COMP 229"),
            ClassGroup(
                ClassGroup(
                    SingleClass("MATH 210"),
                    SingleClass("MATH 214"),
                    op=Operator.And,
                ),
                SingleClass("COMP 149"),
                op=Operator.Or,
            ),
            ClassGroup(
                SingleClass("COMP 146"),
                SingleClass("MATH 150"),
                op=Operator.Or,
            ),
            op=Operator.And,
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_ignore_first_operator(self):
        input = ["and 1", "or 2", "or 3"]

        expected = ClassGroup(
            SingleClass("1"), SingleClass("2"), SingleClass("3"), op=Operator.Or
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_ignore_group_first_operator(self):
        input = ["( and 1", "or 2)"]

        expected = ClassGroup(SingleClass("1"), SingleClass("2"), op=Operator.Or)

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())

    def test_simple_2(self):
        input = [
            "( 1",
            "and 2",
            "and 3)",
            "( and 4",
            "or 5)",
        ]

        expected = ClassGroup(
            ClassGroup(
                SingleClass("1"),
                SingleClass("2"),
                SingleClass("3"),
                op=Operator.And,
            ),
            ClassGroup(
                SingleClass("4"),
                SingleClass("5"),
                op=Operator.Or,
            ),
            op=Operator.And,
        )

        parsed = parse_prerequisite_list(input)

        self.assertEqual(parsed.to_json(), expected.to_json())


if __name__ == "__main__":
    unittest.main()
