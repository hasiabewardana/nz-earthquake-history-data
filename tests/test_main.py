import unittest


class TestGreet(unittest.TestCase):
    def test_greet(self):
        self.assertEqual("", "Hi, PyCharm")


if __name__ == "__main__":
    unittest.main()
