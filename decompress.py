
# decompress.py
# Jacob Reppeto

from typing import Optional
from argparse import ArgumentParser

from BinaryFileIO import *

def decompressFile(compressedFile: str, decompressedFile: str):
    """
    Decompress file using Huffman compression algorithm.

    File format written by compress.py:

    Header:
    - 32 bits (unsigned integer): number of bytes in original file
    - 16 bits (unsigned short integer): number of unique characters
    - For each unique character:
        * 8 bits (unsigned byte): character value (ord(character))
        * 8 bits (unsigned byte): number of bits in its Huffman code
        * variable bits: the Huffman code itself, written as bits and
          padded with zeros up to the next 8-bit boundary (shared bit stream)

    Data:
    - Huffman codes for each original byte, written back-to-back as bits;
      final partial byte padded with zeros.

    :param compressedFile: path to compressed file
    :param decompressedFile: path of decompressed file to create
    :return: None
    """
    # reader for compressed file
    reader = BinaryFileReader(compressedFile)

    #---- Read Header ----#

    # read total number of bytes in original file
    totalBytes = reader.readUInt()

    # read number of unique characters
    uniqueChars = reader.readUShort()

    #reconstruct huffman code dictionary
    codeDict = {}
    for _ in range(uniqueChars):

        # read character value
        charValue = reader.readUByte()
        character = chr(charValue)

        # read length of huffman code in bits
        codeLength = reader.readUByte()

        # read huffman code bits to then add to code dictionary
        bits = ""
        for _ in range(codeLength):
            bit = reader.readBit()
            bits += str(bit)
        code = "".join(bits)
        codeDict[code] = character

    #---- End Read Header ----#

    #---- Decompression Data ----#

    # write decompressed data to output file
    with open(decompressedFile, "w") as outfile:
        currentCode = ""
        bytesWritten = 0

        # read bits until all original bytes are written
        while bytesWritten < totalBytes:
            bit = reader.readBit()
            currentCode += str(bit)

            # check if current code matches any character
            if currentCode in codeDict:
                character = codeDict[currentCode]
                outfile.write(character)
                bytesWritten += 1
                currentCode = ""
    #---- End Decompression Data ----#



def main():
    parser = ArgumentParser(description="decompress file using Huffman compression algorithm")
    parser.add_argument("file", help="file to decompress")
    parser.add_argument("decompressedFile", nargs="?", default=None,
                        help="name of decompressed file to create; defaults to removing .hc suffix if not supplied or using .dc if no .hc suffix at end")
    args = parser.parse_args()

    fileToDecompress = args.file
    decompressedFile = args.decompressedFile
    if decompressedFile is None:
        if fileToDecompress[-3:] == ".hc":
            decompressedFile = fileToDecompress[:-3]
        else:
            decompressedFile = fileToDecompress + ".dc"

    decompressFile(fileToDecompress, decompressedFile)

if __name__ == '__main__':
    main()