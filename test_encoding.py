import unittest
from encoding import PngEncoder
import random

class TestEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = PngEncoder('TEST_SEED')

    def test_seed(self):
        self.assertEqual(self.encoder._seed, 'TEST_SEED')

    def test_random_shift(self):
        """Test that a list of values can be encoded and decoded"""
        values = [0, 1, 31, 32, 64, 127, 127, 255]
        # Set the seed and encode
        random.seed(self.encoder._seed)
        shifted = []
        for i in values:
            shifted.append(self.encoder._random_shift(i))
            print(shifted)
        # Reset seed and decode
        random.seed(self.encoder._seed)
        unshifted = []
        for i in shifted:
            unshifted.append(self.encoder._random_shift(i, direction=-1))

        self.assertEqual(unshifted, values)
    
