import unittest

import prereq_parser as prereq

# prerequisites = [['Math 120', 'or Math 124', 'or Math 128', 'or APBC', 'or OXMA'], ['and Phys 120', 'or Phys 125', 'or APPE']]
# prerequisites = ['Math 101', 'and Math 100', 'and Math 201']
prerequisites = ['1', 'and 2', 'and 3', 'or 4']

class TestPrerequiteParsing(unittest.TestCase):

    def testParenthesies(self):

        # General parenthesies test
        self.assertEqual(prereq.parseParenthesies(['( 1', '2', '3)', '(1', '2)', '5']), [['1', '2', '3'], ['1', '2'], '5'])

        # Test for insane levels of grouping
        # self.assertEqual(prereq.parseParenthesies(['((((1', '2)', '3)', '4)', '5)']), [[[[['1', '2'], '3'], '4'], '5']])

        # Test that unclosed parenthesies just select the rest of the requirements
        self.assertEqual(prereq.parseParenthesies(['(1', '2)', '(1', '2', '3']), [['1', '2'], ['1', '2', '3']])

        # Test that the function will not change a function with no parenthesies
        self.assertEqual(prereq.parseParenthesies(['1', '2', '3']), ['1', '2', '3'])

    def testAddingOperators(self):

        # Test that the correct template for the courses are generated
        self.assertEqual(prereq.addOperator("and", [prereq.addCourse('1'), prereq.addCourse('2'), prereq.addCourse('3')]), {
            "type": "and",
            "nested": [
                {
                    "type": "course",
                    "course": "1"
                },
                {
                    "type": "course",
                    "course": "2"
                },
                {
                    "type": "course",
                    "course": "3"
                }
            ]
        })

        self.assertEqual(prereq.addOperator("and"), {
            "type": "and",
            "nested": []
        })

    def testLogicParser(self):

        # Test that the logic parser works
        self.assertEqual(prereq.getOperators(['1', 'and 1', ['and 2', 'and 3', 'and 4'], 'or 5']), ['and', 'and', ['and', 'and', 'and'], 'or'])

    def testStrippingOperators(self):

        # Test that stripping off the text of the operator works
        self.assertEqual(prereq.stripOperator('and 1'), '1')

        self.assertEqual(prereq.stripOperator(' and 2'), '2')

    def testPrereq1(self):

        self.assertEqual(prereq.parse(["1", "and 2", "and 3", "or 4"]),

        {
            "type": "or",
            "nested": [
                {
                    "type": "course",
                    "course": "4"
                },
                {
                    "type": "and",
                    "nested": [
                        {
                            "type": "course",
                            "course": "1"
                        },
                        {
                            "type": "course",
                            "course": "2"
                        },
                        {
                            "type": "course",
                            "course": "3"
                        }
                    ]
                }
            ]
        })

    def testPrereq2(self):

        self.assertEqual(prereq.parse(['Math 101', 'and Math 100', 'and Math 201']),

        {
            "type": "and",
            "nested": [
                {
                    "type": "course",
                    "course": "Math 101"
                },
                {
                    "type": "course",
                    "course": "Math 100"
                },
                {
                    "type": "course",
                    "course": "Math 201"
                }
            ]
        })

    def testPrereq3(self):

        # Phys 266
        self.assertEqual(prereq.parse(['( PHYS 110', 'or PHYS 115', 'or APPM', 'or OXPE)', '(and PHYS 120', 'or PHYS 125', 'or PHYS 230', 'or APPE)']),

        {
            "type": "and",
            "nested": [
                {
                    "type": "or",
                    "nested": [
                        {
                            "type": "course",
                            "course": "PHYS 110"
                        },
                        {
                            "type": "course",
                            "course": "PHYS 115"
                        },
                        {
                            "type": "course",
                            "course": "APPM"
                        },
                        {
                            "type": "course",
                            "course": "OXPE"
                        }
                    ]
                },
                {
                    "type": "or",
                    "nested": [
                        {
                            "type": "course",
                            "course": "PHYS 120"
                        },
                        {
                            "type": "course",
                            "course": "PHYS 125"
                        },
                        {
                            "type": "course",
                            "course": "PHYS 230"
                        },
                        {
                            "type": "course",
                            "course": "APPE"
                        }
                    ]
                }
            ]
        }

        )

if __name__ == "__main__":
    unittest.main()
