from unittest import TestLoader, TextTestRunner

tests = TestLoader().discover('./tests')
result = TextTestRunner(verbosity=20).run(tests)