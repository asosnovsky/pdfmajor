# API

The library is constructed from 4 base modules:

 * **lexer**: contains low-level classes for tokenization
 * **pdf_parser**: a parser based on the tokens that attempts to map pdf values to python values
 * **xref**: a database for caching indirect objects in memory
 * **filters**: a decryption module for decoding pdf-streams
 * **fonts**: a font's database and evaluation module
 * **document**: top-level abstraction to be used by end users



