# A simple python bytecode assembler
import sys
import os
import ntpath
import ast
import dis
import types
import re
import marshal
import time
import struct


class PyBy:
    def __init__(self, fname, src):
        self.fname = fname
        self.target_fname = os.path.splitext(fname)[0] + ".pyc"
        self.src = src
        self.directives = [ln for ln in src if len(ln) > 1 and ln[0] == "#"]
        self.code = [ln for ln in src if ln not in self.directives]
        self.bytecode = []
        self.code_obj = None
        self.code_defs = {
            "argcount": 0,
            "nlocals": 0,
            "stacksize": 0,
            "flags": 0x0000,
            "consts": (),
            "names": (),
            "varnames": (),
            "name": "",
            "firstlineno": 1,
            "lnotab": bytes(),
            "freevars": (),
            "cellvars": (),
        }

    def init_constants(self):
        for defn in self.directives:
            match = re.match(r"^\#define\s+(\w+)\s+(.*)$", defn)
            if match:
                name, value = match.groups()
                if name not in self.code_defs:
                    self.__raise_err("Unexpected directive: %s" % name)
                else:
                    self.code_defs[name] = ast.literal_eval(value)

    def gen_bytecode(self):
        for ln in self.code:
            val = ln.split()
            if val:
                instr = val[0].upper()
                if instr in dis.opmap:
                    if len(val) > 1:
                        ins = [dis.opmap[instr], int(val[1]), 0]
                        self.bytecode.extend(ins)
                    else:
                        self.bytecode.append(dis.opmap[instr])
                else:
                    self.__raise_err("Unknown instruction: %s" % val[0])

    def gen_PyObj(self):
        self.code_obj = types.CodeType(
            self.code_defs["argcount"],
            self.code_defs["nlocals"],
            self.code_defs["stacksize"],
            self.code_defs["flags"],
            self.__to_bytes(),
            self.code_defs["consts"],
            self.code_defs["names"],
            self.code_defs["varnames"],
            self.fname,
            self.code_defs["name"],
            self.code_defs["firstlineno"],
            self.code_defs["lnotab"],
            self.code_defs["freevars"],
            self.code_defs["cellvars"],
        )

    def eval(self):
        print "Evaluating code object"
        res = eval(self.code_obj)
        print "The python bytecode VM exited with return value %s" % res

    def write_file(self):
        try:
            dmpfile = open(self.target_fname, "wb")
            dmpfile.write(b"\x0a\xf3\x0d\x0a")  # Magic no
            timestamp = int(time.time())
            dmpfile.write(struct.pack("<I", timestamp))  # Timestamp
            dmpfile.write(marshal.dumps(self.code_obj))
            dmpfile.close()
        except IOError as e:
            self.__raise_err('Unexpected IOError %d: %s' % (e.errno, e.strerror))

    def run(self):
        print 'Initializing directives... ',
        self.init_constants()
        print 'Done.'

        print 'Assembling instructions... ',
        self.gen_bytecode()
        print 'Done.'

        print 'Generating Python Code object... ',
        self.gen_PyObj()
        print 'Done.'

        print 'Writing to file... ',
        self.write_file()
        print 'Done.'

        print 'Sucessfully assembled and saved to %s' % self.target_fname


    def __to_bytes(self):
        return "".join(map(chr, self.bytecode))

    def __raise_err(self, msg):
        print 'ERROR!'
        print '\t' + msg
        sys.exit(-2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Need atleast 1 argument to run"
        sys.exit(-1)

    try:
        file = open(sys.argv[1], "r")
        src = file.read().splitlines()
        file.close()
        print 'PyBy: The python bytecode assembler'
        print 'Assembling %s' % sys.argv[1]
        asm = PyBy(ntpath.basename(sys.argv[1]), src)
        asm.run()

    except IOError:
        print "The specified file is not found: %s" % sys.argv[1]
