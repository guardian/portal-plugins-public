from __future__ import absolute_import
import unittest


class TestHumanFriendly(unittest.TestCase):
    def test_should_match(self):
        from gnmpagerduty.tasks import human_friendly

        self.assertEqual(human_friendly(8589934592),"8.0GiB")
        self.assertEqual(human_friendly(17592186044416),"16.0TiB")
        self.assertEqual(human_friendly(28037546508288),"25.5TiB")

