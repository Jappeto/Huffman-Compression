# BinaryFileIO.py
# Jacob Reppeto
# ----------------------------------------------------------------------

import struct

# ----------------------------------------------------------------------

class BinaryFileWriter:

    # ------------------------------------------------------------------

    def __init__(self, filename: str):
        """
        open file for writing in binary format
        :param filename: path of file to create/open
        """
        self.outfile = open(filename, "wb")
        self.bitValue = 0
        self.numberOfBits = 0

    # ------------------------------------------------------------------

    def writeUByte(self, value: int):
        """
        write value (0-255) to file as 8 bits
        :param value: integer value 0 to 255 to write
        :return: None
        """

        assert 0 <= value < 256

        self.__flushBits()
        s = struct.pack('<B', value)
        self.outfile.write(s)

    # ------------------------------------------------------------------

    def writeUShort(self, value: int):
        """
        write value (0-65535) to file as 16 bits
        :param value: integer value 0 to 655335 to write
        :return: None
        """

        assert 0 <= value < 65536

        self.__flushBits()
        s = struct.pack('<H', value)
        self.outfile.write(s)

    # ------------------------------------------------------------------

    def writeUInt(self, value: int):

        """
        write value (0 to 2**32 - 1) to file as 32 bits
        :param value: integer value 0 to 2**32 - 1 to write
        :return: None
        """

        assert 0 <= value < 2 ** 32

        self.__flushBits()
        s = struct.pack('<I', value)
        self.outfile.write(s)

    # ------------------------------------------------------------------

    def writeBit(self, bit: int, flushByte: bool = False):
        """
        write a single bit to file
        :param bit: 0 or 1 to write to file
        :param flushByte: whether or not to finish this group of 8 bits
        :return: None
        """
        assert bit == 0 or bit == 1
        self.bitValue = (self.bitValue << 1) + bit
        self.numberOfBits += 1
        if self.numberOfBits == 8 or flushByte:
            self.__flushBits()

    # ------------------------------------------------------------------

    def __flushBits(self):
        """
        helper method to finish writing bits to file
        :return: None
        """
        # if some data to write
        if self.numberOfBits != 0:
            # shift bits to left so data is in leftmost bits and rightmost bits that are not part of data are zero
            self.bitValue = self.bitValue << (8 - self.numberOfBits)
            # reset for next bits to be written and prevents infinite recursion
            self.numberOfBits = 0
            # write data
            self.writeUByte(self.bitValue)
            self.bitValue = 0

    # ------------------------------------------------------------------

    def close(self):
        """
        close the file so all data is written
        :return: None
        """
        self.__flushBits()
        self.outfile.close()

    # ------------------------------------------------------------------

# ----------------------------------------------------------------------

class BinaryFileReader:

    def __init__(self, filename: str):
        """
        open a file for reading as binary data
        :param filename: path to file to open
        """
        self.infile = open(filename, "rb")
        self.bitValue = 0
        self.numberOfBits = 0

    # ------------------------------------------------------------------

    def readUByte(self) -> int:
        """
        read 8 bits from file
        :return: value of the 8 bits read from 0 to 255
        """
        self._resetBits()
        s = self.infile.read(1)
        if len(s) != 1:
            raise ValueError("ReadBitFile.readUInt error")
        v = struct.unpack('<B', s)[0]
        return v

    # ------------------------------------------------------------------

    def readUShort(self) -> int:
        """
        read 16 bits from file
        :return: value of the 16 bits read from 0 to 65535
        """
        self._resetBits()
        s = self.infile.read(2)
        if len(s) != 2:
            raise ValueError("ReadBitFile.readUInt error")
        v = struct.unpack('<H', s)[0]
        return v

    # ------------------------------------------------------------------

    def readUInt(self) -> int:
        """
        read 32 bits from file
        :return: value of the 32 bits read from 0 to 2**32 - 1
        """
        self._resetBits()
        s = self.infile.read(4)
        if len(s) != 4:
            raise ValueError("ReadBitFile.readUInt error")
        v = struct.unpack('<I', s)[0]
        return v

    # ------------------------------------------------------------------

    def readBit(self) -> int:
        """
        read a single bit from file
        :return: 0 or 1 that was read
        """

        # if no bits remaining in the byte we read, read a new byte
        if self.numberOfBits == 0:
            self.bitValue = self.readUByte()
            self.numberOfBits = 8

        # get the left most bit
        b = (self.bitValue & 128) >> 7
        # shift so leftmost bit is ready for next call
        self.bitValue = (self.bitValue << 1)
        self.numberOfBits -= 1
        return b

    # ------------------------------------------------------------------

    def _resetBits(self):
        """
        helper method to start reading bits again
        :return:
        """
        self.bitValue = 0
        self.numberOfBits = 0

    # ------------------------------------------------------------------

    def close(self):
        """
        close the file
        :return: None
        """
        self.infile.close()

    # ------------------------------------------------------------------

# ----------------------------------------------------------------------