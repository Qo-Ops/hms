import unittest

from app import app


class LoginTestCase(unittest.TestCase):

    def setUp():
        app.config['TESTING'] = True

    def tearDown():
        pass


if __name__ == '__main__':
    unittest.main()
