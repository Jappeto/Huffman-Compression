# compress.py
# Jacob Reppeto


from __future__ import annotations
from argparse import ArgumentParser
from BinaryFileIO import BinaryFileWriter

class huffmanNode:
    """
    Node for the Huffman tree
    Attributes:
    char: character stored in the node
    frequency: frequency of the character
    left: left child node
    right: right child node
    """
    def __init__(self, char, freq, left = None, right = None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right= right

    def __lt__(self, other: huffmanNode) -> bool:
        return self.freq < other.freq


def huffmanTree(inputFilename: str):
    """
    builds huffman tree from input file
    :param inputFilename: file to build huffman tree from
    :return: root of huffman tree
    """
    # open the file and build frequency dictionary
    with open(inputFilename, "r") as infile:
        freq = {}
        for line in infile:
            for char in line:
                if char in freq:
                    freq[char] += 1
                else:
                    freq[char] = 1

    # run through the frequency dictionary and create a priority queue
    priorityQueue = []
    for char, frequency in freq.items():
        node = huffmanNode(char, frequency)
        priorityQueue.append(node)
    priorityQueue.sort()

    # build the huffman tree
    while len(priorityQueue) != 1:

        # remove the two nodes of lowest frequency
        left = priorityQueue.pop(0)
        right = priorityQueue.pop(0)

        # create a new internal node with these two nodes as children`
        total = left.freq + right.freq
        node = huffmanNode(None, total, left, right)
        priorityQueue.insert(0, node)
        priorityQueue.sort()

    root = priorityQueue[0]

    return root, freq

def traverseTree(node: huffmanNode, code: str, codeDict: dict[str, str]):
    """
    traverse the huffman tree using pre-order traversal to build code dictionary
    0 for left, 1 for right
    :param node: current node in the huffman tree
    :param code: current code string
    :param codeDict: dictionary to store codes (character: bits)
    :return: None
    """

    # if leaf node, add to code dictionary
    if node.left is None and node.right is None:
        # handle edge case of single character file
        if code == "":
            code = "0"

        # add character and code to dictionary
        codeDict[node.char] = code
        return

    # traverse left and right children
    traverseTree(node.left, code + "0", codeDict)
    traverseTree(node.right, code + "1", codeDict)


def compressFile(inputFilename: str, outputFilename: str, root: huffmanNode, freq: dict[str, int]):
    """
    compress the input file using the huffman tree and then write it output file.
    must add a header to the output file that contains the frequency dictionary
    Header format:
    - 32 bits (unsigned integer): number of bytes in original file
    - 16 bits (unsigned short integer): number of unique characters
    - For each unique character:
    * 8 bits (unsigned byte): character value (ord(character))
    * 8 bits (unsigned byte): number of bits in its Huffman code
    * variable bits: the Huffman code itself, written as bits and padded
    with zeros up to the next 8-bit boundary
    - Then the compressed data stream: Huffman codes for each original byte,
    written back-to-back as bits; final partial byte padded with zeros.
    :param inputFilename: file to compress
    :param outputFilename: file to write compressed data to
    :param root: root of huffman tree
    :param freq: frequency dictionary
    :return: None
    """

    # build code dictionary dict[character] = bits
    codeDict = {}
    traverseTree(root, "", codeDict)

    #-------- Header --------#

    # store total number of bytes in original file
    totalBytes = sum(freq.values())

    #store number of unique characters
    uniqueChars = len(freq)

    writer = BinaryFileWriter(outputFilename)

    # write total bytes and unique characters to output file
    writer.writeUInt(totalBytes)
    writer.writeUShort(uniqueChars)

    # write each character and its huffman code to header for output file
    for char, code in codeDict.items():

        # write character value
        writer.writeUByte(ord(char))

        # write length of huffman code in bits
        codeLength = len(code)

        # use writeUByte as code length is at most 255
        writer.writeUByte(codeLength)

        # write huffman code bits
        for bit in code:
            if bit == "0":
                writer.writeBit(0)
            else:
                writer.writeBit(1)

    #-------- End Header --------#

    #-------- Compression Data --------#
    # write compression data to output file
    with open(inputFilename, "r") as infile:
        for line in infile:
            for char in line:
                code = codeDict[char]
                for bit in code:
                    if bit == "0":
                        writer.writeBit(0)
                    else:
                        writer.writeBit(1)

    writer.close()
    #-------- End Compression Data --------#




def main():
    parser = ArgumentParser(description="compress file using Huffman compression algorithm")
    parser.add_argument("file", help="file to compress")
    parser.add_argument("compressedFile", nargs="?", default=None, help="name of compressed file to create; defaults to adding .hc suffix if not supplied")
    args = parser.parse_args()

    fileToCompress = args.file
    root, freq = huffmanTree(fileToCompress)
    compressedFile = args.compressedFile
    if compressedFile is None:
        compressedFile = fileToCompress + ".hc"

    compressFile(fileToCompress, compressedFile, root, freq)



if __name__ == '__main__':
    main()