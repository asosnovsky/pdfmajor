"""A PDF token parser
    this parser parses the bytes in three steps
    1. Generate tokens from the byte stream using the PDFLexer
    2. Level 1 Parsing: Match Low level objects such as primitive types, arrays, dictionaries
    3. Level 2 Parsing: Match high level objects such as Streams and Indirect objects
"""
