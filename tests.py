# -*- coding: utf-8 -*-
import os
import unittest
import codecs

from atomicfile import AtomicFile
from atomicfile import open_atomic


def create_test_file(filename, content=b'test\n', mode=None):
    f = open(filename, "wb")
    f.write(content)
    f.close()
    if mode is not None:
        os.chmod(filename, mode)


class AtomicFileTest(unittest.TestCase):
    def setUp(self):
        self.filename = "test-atomicfile.txt"

    def test_write(self):
        create_test_file(self.filename)
        af = AtomicFile(self.filename)
        expected = b"this is written by AtomicFile.\n"
        af.write(expected)
        af.close()

        f = open(self.filename, "rb")
        result = f.read()
        f.close()
        try:
            self.assertEqual(result, expected)
        finally:
            os.remove(self.filename)

    def test_close(self):
        af = AtomicFile(self.filename)
        af.write(b"test\n")
        af.close()
        try:
            af.write(b"test again\n")
            self.fail('ValueError not raised')
        except ValueError:
            pass
        finally:
            os.remove(self.filename)

    def test_with(self):
        data = b"this is written by AtomicFile.\n"

        with AtomicFile(self.filename) as f:
            f.write(data)

        try:
            f.write(data)
            self.fail("'ValueError: I/O operation on closed file' not raised")
        except ValueError:
            pass
        finally:
            os.remove(self.filename)

    def test_open_atomic(self):
        create_test_file(self.filename)
        af = open_atomic(self.filename)
        expected = b"this is written by AtomicFile from open_atomic.\n"
        af.write(expected)
        af.close()

        f = open(self.filename, "rb")
        result = f.read()
        f.close()
        try:
            self.assertEqual(result, expected)
        finally:
            os.remove(self.filename)

    def test_open_invalid_mode(self):
        create_test_file(self.filename)
        try:
            open_atomic(self.filename, mode="a")
            self.fail("'TypeError: Invalid mode did not raise error")
        except TypeError:
            pass
        finally:
            os.remove(self.filename)

    def test_permissions_1(self):
        expected_mode = 0o341
        create_test_file(self.filename, mode=expected_mode)

        af = AtomicFile(self.filename)
        af.write(b"I don't really care of the content.\n")
        af.close()

        st_mode = os.lstat(self.filename).st_mode & 0o777

        # On Windows only the Owner write bit (0200) are writable
        if os.name == "nt":
            st_mode &= 0o200
            expected_mode &= 0o200

        try:
            self.assertEqual(st_mode, expected_mode)
        finally:
            os.remove(self.filename)

    def test_permissions_2(self):
        expected_mode = 0o541
        create_test_file(self.filename, mode=expected_mode)

        af = AtomicFile(self.filename)
        af.write(b"I don't really care of the content.\n")
        af.close()

        st_mode = os.lstat(self.filename).st_mode & 0o777

        # On Windows only the Owner read/write bits (0600) are writable
        if os.name == "nt":
            st_mode &= 0o200
            expected_mode &= 0o200

        try:
            self.assertEqual(st_mode, expected_mode)
        finally:
            os.chmod(self.filename, 0o666)
            os.remove(self.filename)

    def test_encoding(self):
        data = u"Unicode Capit\xe1n is written by AtomicFile.\n"
        encoding = "utf-8"
        af = AtomicFile(self.filename, "wb", encoding=encoding)
        af.write(data)
        af.close()

        f = codecs.open(self.filename, "rb", encoding=encoding)
        decoded_result = f.read()
        f.close()
        f = open(self.filename, "rb")
        raw_result = f.read()
        f.close()

        try:
            self.assertEqual(data, decoded_result)
            self.assertEqual(data.encode(encoding), raw_result)
        finally:
            os.remove(self.filename)


if __name__ == "__main__":
    unittest.main()
