import unittest
from encoding import PngEncoder
import random

class TestEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = PngEncoder('TEST_SEED')

    def test_seed_init(self):
        """Test that the Seed supplied in the constructer gets assigned correctly"""
        self.assertEqual(self.encoder._seed, 'TEST_SEED')

    def test_random_shift_difference(self):
        """Test that a list of values can be encoded and decoded"""
        values = [0, 1, 31, 32, 64, 127, 127, 255]
        # Set the seed and encode
        random.seed(self.encoder._seed)
        shifted = []
        for i in values:
            shifted.append(self.encoder._random_shift(i))
        self.assertNotEqual(shifted, values)
    def test_random_unshift(self):
        """Test that a list of values can be encoded and decoded"""
        values = [0, 1, 31, 32, 64, 127, 127, 255]
        # Set the seed and encode
        random.seed(self.encoder._seed)
        shifted = []
        for i in values:
            shifted.append(self.encoder._random_shift(i))
        # Reset seed and decode
        random.seed(self.encoder._seed)
        unshifted = []
        for i in shifted:
            unshifted.append(self.encoder._random_shift(i, direction=-1))

        self.assertEqual(unshifted, values)
    
    def test_seed_incompatibility(self):
        """Test that decoding with a different seed yields an incorrect result"""
        values = [0, 1, 31, 32, 64, 127, 127, 255]
        # Set the seed and encode
        random.seed(self.encoder._seed)
        shifted = []
        for i in values:
            shifted.append(self.encoder._random_shift(i))
        # Use a different seed to decode
        random.seed('different')
        unshifted = []
        for i in shifted:
            unshifted.append(self.encoder._random_shift(i, direction=-1))

        self.assertNotEqual(unshifted, values)

    def test_encode_decode(self):
        """Test that data supplied to the encoder can be decoded to the same values"""
        inputs = [
            '',
            ' ',
            '''
            ''',
            'Hello, world!',
            'Привет, мир!',
            'こんにちは世界！',
            '{"name":"John", "age":30, "cars":[ "Ford", "BMW", "Fiat" ]}',
            '''<!DOCTYPE html>
                <html>
                <body>
                    <h1>My First Heading</h1>
                    <p>My first paragraph.</p>
                </body>
                </html>''',
            'x = (−b ± b2 − 4ac) / √2a',
            '̫͚̯͈̯ͅḬ̺̥̙͠nv̧̲̳̲o̴͚͇̬͈k͏̠̙̼̺̬̳̝i̴̗̺̬̠n҉͎̩g̺̝͉̹ t̞̞̱̜̟͓̟h͖̠͍̩͡e ̫̬̣̣̙̳͠ͅf͏̥̜̤̩̙̻̩e̦̫ͅe̴͚̖̝̱ͅl̪̩̭i҉͎̱̗̖̭̱ͅn̺̗͉̦̠͇͞g͖̰̲͍̙̫͇͞ ̻͇̭o̘̳̤͖͈̤f̳͘ ͕c̴̠h̰̞̬͍͔̖͙a͙͍̫͍ͅo͙̮s͖͙̼̙̘͍̣.͚',
            'ʁɷȾŸ—ξϷЈϿ�',
            '😀🤪🤔😷🤤😱😼❤👋👏👩‍⚕️💰⛏🇬🇧⁉'
        ]
        for i in inputs:
            with self.subTest(i=i):
                encoded_image = self.encoder.encode_as_image(i)
                encoded_pixels = self.encoder._pixel_value_generator(encoded_image.getdata()) # Makes PIL Image iterable
                decoded_characters = self.encoder.decode_image_bytes(encoded_pixels)
                decoded_data = ''.join(decoded_characters)
                self.assertEqual(decoded_data, i)

    def test_encode_uses_seed(self):
        """Test that decoding with the wrong seed yields the wrong result"""
        i = 'Hello, world!'
        encoded_image = self.encoder.encode_as_image(i)
        encoded_pixels = self.encoder._pixel_value_generator(encoded_image.getdata()) # Makes PIL Image iterable
        # Change the seed before decoding
        self.encoder._seed = 'Wrong seed'
        decoded_characters = self.encoder.decode_image_bytes(encoded_pixels)
        decoded_data = ''.join(decoded_characters)
        self.assertNotEqual(decoded_data, i)