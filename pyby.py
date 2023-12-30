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
            "stacksize": 0,
            "flags": 0x0000,
            "consts": [None],
            "names": [],
            "varnames": [],
            "name": "",
            "firstlineno": 1,
            "lnotab": bytes(),
            "freevars": (),
            "cellvars": (),
        }
        self.const_table = {'None': 0}
        self.name_table = {}
        self.var_table = {}

    def init_constants(self):
        for defn in self.directives:
            match = re.match(r"^\#define\s+(\w+)\s+(.*)$", defn)
            if match:
                name, value = match.groups()
                if name not in self.code_defs:
                    self.__raise_err("Unexpected directive: %s" % name)
                else:
                    self.code_defs[name] = ast.literal_eval(value)

            match = re.match(r"^\#const\s+(\w+)\s+(.*)$", defn)
            if match:
                cname, cval = match.groups()
                cval = ast.literal_eval(cval)
                if cval not in self.code_defs['consts']:
                    self.code_defs['consts'].append(cval)
                self.const_table[cname] = self.code_defs['consts'].index(cval)

            match = re.match(r"^\#defn\s+(.*)$", defn)
            if match:
                matched = re.split(r',\s*', match.group(1))
                fn_names = ', '.join('"{0}"'.format(w) for w in matched)
                self.code_defs["names"] = tuple(ast.literal_eval(fn_names))
                self.name_table = {v: k for k, v in dict(enumerate(self.code_defs['names'])).items()}

            match = re.match(r"^\#defvar\s+(.*)$", defn)
            if match:
                matched = re.split(r',\s*', match.group(1))
                var_names = ', '.join('"{0}"'.format(w) for w in matched)
                self.code_defs["varnames"] = tuple(ast.literal_eval(var_names))
                self.var_table = {v: k for k, v in dict(enumerate(self.code_defs['varnames'])).items()}


    def gen_bytecode(self):
        for ln in self.code:
            val = ln.split()
            if val and val[0][0] != '%':
                instr = val[0].upper()
                if instr in dis.opmap:
                    if len(val) > 1:
                        if re.match(r'[A-Z0-9]+_CONST', instr):
                            arg = self.const_table[val[1]]
                        elif re.match(r'[A-Z0-9]+_GLOBAL', instr):
                            arg = self.name_table[val[1]]
                        elif re.match(r'[A-Z0-9]+_FAST', instr):
                            arg = self.var_table[val[1]]
                        else:
                            arg = int(val[1])

                        ins = [dis.opmap[instr], arg, 0]
                        self.bytecode.extend(ins)
                    else:
                        self.bytecode.append(dis.opmap[instr])
                else:
                    self.__raise_err("Unknown instruction: %s" % val[0])

    def gen_PyObj(self):
        self.code_obj = types.CodeType(
            self.code_defs["argcount"],
            len(self.code_defs["varnames"]),
            self.code_defs["stacksize"],
            self.code_defs["flags"],
            self.__to_bytes(),
            tuple(self.code_defs["consts"]),
            tuple(self.code_defs["names"]),
            tuple(self.code_defs["varnames"]),
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
