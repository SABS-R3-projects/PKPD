import src.PKPD.models.inc_dec as inc_dec    # The code to test

import unittest
from hypothesis import given, settings
import hypothesis.strategies as st

def test_increment():
    assert inc_dec.increment(3) == 4

def test_decrement():
    assert inc_dec.decrement(3) == 2

class TestSimple(unittest.TestCase):
    # @ given ( x = st . integers ()) # Wrong range !
    @given(x = st.integers(min_value = 0, max_value = 1114111))
    def test_ord_inverts_chr(self, x):
        assert ord(chr(x)) == x