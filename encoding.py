import math
from PIL import Image
from io import BytesIO
import random

class PngEncoder:
    def __init__(self, seed=None):
        self._seed = seed

    def _random_shift(self, value, direction=1):
        """Takes a value between 0 and 255 and randomises it to a different value. 
            If direction set to -1, then it can unshift previously shifted values (assuming the same random seed was initialised each time) """
        shift_factor = random.randint(0, 255)
        shifted = (value + direction*shift_factor) % 256
        return shifted

    def encode_as_image(self, data):
        """Saves UTF-8 encoded text into a PNG file.
            Works on the premise that UTF-8 encodes data into 8-bit chunks,
            and a PNG image can be seperated out into 0-255 encoded color values
            i.e 0 = 00000000 whereas 255 = 11111111"""
        random.seed(self._seed)
        data_bytes = bytes(data, encoding='utf-8')
        size = math.ceil(math.sqrt(len(data_bytes)/3)) # Calculate how big of image is needed
        img = Image.new('RGB', (size, size))
        x, y = 0, 0
        for i in range(0, len(data_bytes), 3):
            # Each pixel takes 3 values (RGB) between 0 and 255
            first = data_bytes[i]
            second = data_bytes[i+1] if i + 1 < len(data_bytes) else 0
            third = data_bytes[i+2] if i + 2 < len(data_bytes) else 0
            pixel = (self._random_shift(first), self._random_shift(second), self._random_shift(third))

            # Put pixel into next available slot in image space
            img.putpixel((x, y), pixel)
            if x + 1 == size:
                x = 0
                y += 1
            else:
                x += 1
        return img
    def decode_image_bytes(self, pixel_values):
        """Decodes bytes in PIL PNG file into utf-8 string"""   
        random.seed(self._seed)
        output = []
        end_of_file = False
        values = [] # list outside loop so that excess data can be recovered if end_of_file triggers mid character
        while not end_of_file:
            try:
                values = [] # Reset the saved pixel values
                first = self._random_shift(next(pixel_values), direction=-1)
                if not first: # If first byte is 0, there is nothing left to decode
                    break
                values.append(first)
                if first > 127: # First byte is 110XXXXX or greater, so at least 1 continuation byte
                    values.append(self._random_shift(next(pixel_values), direction=-1))
                if first > 223: # First byte is 1110XXXX or greater, so at least a second continuation byte
                    values.append(self._random_shift(next(pixel_values), direction=-1))
                if first > 239: # First byte is 11110XXX or greater, so a third continuation byte
                    values.append(self._random_shift(next(pixel_values), direction=-1))

                output.append(bytes(values).decode('utf-8'))

            except StopIteration:
                end_of_file = True
        print('LEFTOVER', values)
        return output
    def _pixel_value_generator(self, image):
        """Unpack the pixel values from their tuples so they can be iterated over"""
        i = 0
        for pixel in image:
            for pixel_value in pixel:
                i += 1
                yield pixel_value
    def decode_png_response(self, image_bytes):
        """Decodes the PNG data requested from Imgur"""
        image = Image.open(BytesIO(image_bytes))
        image_data = iter(image.getdata())
        output = self.decode_image_bytes(self._pixel_value_generator(image_data))
        return output