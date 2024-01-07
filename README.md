# PyBy
A simple assembler for Python Bytecode

# About
PyBy is a simple assembler which takes in python bytecode instructions and produces equivalent .pyc file. This project is written using **Python 2.7**(PyPy) since it has simple and well
documented python bytecode instructions, which is guaranteed to not change over time.

# Things to note
- This project is written as a file of bytecode instructions, comprising of 1 instruction per line.
- Any specified python bytecode instruction can be used. Parameters are seperated using spaces
- Directives are written using `#` character at the start of line and comments using `%` character
- The assembler contains some macros, which help in simplifying many instructions

For more details, refer the project's docs.

# Project Status
This project is still a work-in-progress. While the basic structure is completed, the assembler requires much more higher-level interface and error-handling mechanisms.

# Contribution
Contributors are welcome! To contribute, create a pull request. To report any issues, create a new issue in the github issue tracker.

# Things to do
- [ ] Add more higher-level macros
- [ ] Create a good CLI UI for assembler
- [ ] Add more error-handling mechanisms
- [ ] Add support for inline debugging
- [ ] Add a good API for dynamic generation of bytecode
- [ ] Create docs
