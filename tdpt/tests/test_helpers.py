import unittest

from tdpt.helpers import format_speed

class TestHelpers(unittest.TestCase):

  def test_format_speed_kb(self):
    self.assertEqual(format_speed(1000), "1.0 kB/s")
    self.assertEqual(format_speed(2500), "2.5 kB/s")
    self.assertEqual(format_speed(11501), "11.5 kB/s")
    self.assertEqual(format_speed(999941), "999.9 kB/s")
    self.assertEqual(format_speed(999999), "1000.0 kB/s")

  def test_format_speed_mb(self):
    self.assertEqual(format_speed(1000000), "1.0 MB/s")
    self.assertEqual(format_speed(10050000), "10.1 MB/s")
    self.assertEqual(format_speed(999949999), "999.9 MB/s")
    self.assertEqual(format_speed(1000000000), "1000.0 MB/s")
