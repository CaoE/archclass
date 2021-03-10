
import sys
import argparse
class MIPS(object):
    def __init__(self,inputFile, disassemblyFile,simulationFile):
        self.input = inputFile
        self.disassemblyFile = disassemblyFile;
        self.simulationFile = simulationFile
        self.__codeStart = 64
        self.__indicator = 0
        self.__instLen = 4
        self.__dataStart = 0
        self.__dataEnd = 0
        self.__writeData = ""
        self.__writeSim = ""
        self.__pc = 0
        self.__instSegment = {}
        self.__dataSegment = {}
        self.__regFlie = [0,0,0,0,0,0,0,0,
                          0,0,0,0,0,0,0,0,
                          0,0,0,0,0,0,0,0,
                          0,0,0,0,0,0,0,0]
    def write_file(self, output, file_path):
        try:
            f = open(file_path, "w")
        except:
            print "Can not open file."
            sys.exit(1)
        try:
            f.write(output)
        except:
            print "Can not write file."
            sys.exit(1)
        finally:
            f.close()

    @staticmethod
    def format_opAND_ADD_NOR_SLT_MUL_SUB(inst):
        if(inst[0] == "0"):
            return (int(inst[16:21], 2), int(inst[6:11], 2), "R", int(inst[11:16], 2))
        else:
            return (int(inst[11:16], 2),int(inst[6:11], 2),  "#", int(inst[16:32], 2))


    @staticmethod
    def format_opSLL_SRL_SRA_MULI(inst):
        if(inst[26:32] == "000010" and inst[0:6] == "000000"):
            return ("SRL",int(inst[16:21], 2), int(inst[11:16], 2), int(inst[21:26], 2))
        if(inst[26:32] == "000011" and inst[0:6] == "000000"):
            return ("SRA", int(inst[16:21], 2), int(inst[11:16], 2), int(inst[21:26], 2))
        if(inst[0:6] == "100001"):
            return ("MUL", int(inst[11:16], 2),int(inst[6:11], 2),  int(inst[16:32], 2))
        if(inst[26:32] == "000000" and inst[0:6] == "000000"):
            return (int(inst[16:21], 2), int(inst[11:16], 2), int(inst[21:26], 2))

    @staticmethod
    def format_opJR(inst):
        return (int(inst[6:11], 2))

    @staticmethod
    def format_opJ(inst):
        return 4*int(inst[6:32], 2)


    @staticmethod
    def format_opSWLW(inst):
        return (int(inst[11:16], 2), int(inst[16:32], 2), int(inst[6:11], 2))

    @staticmethod
    def format_opBEQ(inst):
        return (int(inst[6:11], 2), int(inst[11:16], 2), 4*int(inst[16:32], 2))

    @staticmethod
    def format_opBTZ(inst):
        return (int(inst[6:11], 2), 4*int(inst[16:32], 2))

    switch_function_special = {
        #move last bit
        "10000": lambda instruction:"ADD R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction),     #2
        "00100": lambda instruction:"JR R%d"            % MIPS.format_opJR(instruction),
        "10001": lambda instruction:"SUB R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction),     #2
        "00000": lambda instruction:"SLL R%d, R%d, #%d" % MIPS.format_opSLL_SRL_SRA_MULI(instruction),   #SLL NOP
        "00001": lambda instruction: "%s R%d, R%d, #%d" % MIPS.format_opSLL_SRL_SRA_MULI(instruction),
        "10010": lambda instruction:"AND R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction),
        "10011": lambda instruction:"NOR R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction),
        "10101": lambda instruction:"SLT R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction),
        "01011": lambda instruction: "SW R%d, %d(R%d)"  % MIPS.format_opSWLW(instruction),
        "00011": lambda instruction: "LW R%d, %d(R%d)"  % MIPS.format_opSWLW(instruction),
        "00110": lambda instruction: "BREAK"
    }
    switch_instruction = {
        "000000": lambda instruction: MIPS.switch_function_special[instruction[26:31]](instruction),
        "000010": lambda instruction: "J #%d" %MIPS.format_opJ(instruction),
        "000100": lambda instruction: "BEQ R%d, R%d, #%d" % MIPS.format_opBEQ(instruction),
        "000111": lambda instruction: "BGTZ R%d, #%d" % MIPS.format_opBTZ(instruction),
        "000001": lambda instruction: "BLTZ R%d, #%d" % MIPS.format_opBTZ(instruction),
        "011100": lambda instruction: "MUL R%d, R%d, %s%d" % MIPS.format_opAND_ADD_NOR_SLT_MUL_SUB(instruction)
        #"101011": lambda instruction: "SW R%d, %d(R%d)" % MIPS.format_op5(instruction),
        #"100011": lambda instruction: "LW R%d, %d(R%d)" % MIPS.format_op5(instruction),
    }
    switch_first = {
        "0": lambda instruction: MIPS.switch_instruction[instruction[0:6]](instruction),
        "1": lambda instruction: MIPS.switch_function_special[instruction[1:6]](instruction)
    }



    def analyse_instructions(self, code):
        if(code[0:32] == "00000000000000000000000000000000"):
            disassembledData = "NOP"
        else:
            disassembledData = MIPS.switch_first[code[0:1]](code)
        #print disassembledData
        return disassembledData

    def analyse_data(self, code):
        if code[0] == "0":
            return int(code[:], 2)
        else:
            conv = ""
            for bit in code[:]:
                if bit == "0":
                    conv += "1"
                elif bit == "1":
                    conv += "0"
            return -(int(conv, 2)+1)



    def disassemble(self):
        try:
            binaryFile = open(self.input, "r")
        except:
            print "Can not open"
            sys.exit(1)
        try:
            codes = binaryFile.read()
        except:
            print "Can not read"
            sys.exit(1)
        finally:
            binaryFile.close()
        codes = codes.split('\n')
        self.__indicator = self.__codeStart
        flag = False
        for codeLine in codes:
            if flag == False:
                split1, split12, split13, split14, split15, split16 = \
                    codeLine[0:6], codeLine[6:11], codeLine[11:16], codeLine[16:21], codeLine[21:26], codeLine[26:32]
                inst = self.analyse_instructions(codeLine)
                self.__instSegment[self.__indicator] = inst
                self.__writeData += split1 + " " + split12 + " " + split13+ " " +split14+ " " +split15+ " " +split16
                self.__writeData +="\t" + `self.__indicator`+ "\t" + inst + "\n"
                self.__indicator += self.__instLen

                if inst == "BREAK":
                    flag = True
                    self.__dataStart =  self.__indicator
            else:
                data = self.analyse_data(codeLine)
                self.__dataSegment[self.__indicator] = data
                self.__writeData += codeLine + `self.__indicator`+"\t" + `data`+"\n"
                self.__indicator += self.__instLen
        self.__dataEnd = self.__indicator
        print self.__writeData
        self.write_file(self.__writeData, self.disassemblyFile)
    @staticmethod
    def exeSRL(rt, sa):
        global cbit
        cbit = 0
        data = '{:032b}'.format(rt)

        if data[0] == "0":
            return rt >> sa
        else:
            cdata = "1"
            for bit in data[1:]:
                if bit == "0":
                    cdata += "1"
                else:
                    cdata += "0"
            copydata = list(cdata)
            for i in range(31, -1, -1):
                if i == 31:
                    if cdata[i] == "1":
                        cbit = 1
                        copydata[i] = "0"
                elif cbit == 1:
                    if cdata[i] == "1":
                        cbit = 1
                        copydata[i] = "0"
                    else:
                        cbit = 0
                        copydata[i] = "1"
            copydata = ''.join(copydata)
            finaldata = ""
            for i in range(sa):
                finaldata += "0"
            for bit in copydata[:-sa]:
                finaldata += bit
            return (int(finaldata, 2))

    execute_inst = {

        "ADD": lambda op2,op3 : op2 + op3,
        "SUB": lambda op2,op3: op2 - op3,
        #"BREAK": lambda
        #"SW": lambda rt, offset:
        #"LW":
        "SLL": lambda rt, sa: rt << sa,
        "SRL": lambda inst, sa: MIPS.exeSRL(inst, sa),
        "SRA": lambda rt, sa: rt >> sa,
        #"NOP":
        "MUL": lambda op2, op3: op2 * op3,
        "AND": lambda op2, op3: op2 & op3,
        "NOR": lambda op2, op3: op2 ^ op3,
        "SLT": lambda op2, op3: op2 < op3
    }

    def print_simInfo(self, str):
        siminfo = ""
        siminfo += str+"\n\n"
        siminfo += "Registers\n"
        siminfo += "R00:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R16:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n\n" % tuple(self.__regFlie)
        siminfo += "Data"

        for i in range(self.__dataStart, self.__dataEnd, self.__instLen):
            if (i - self.__dataStart) % (self.__instLen * 8) == 0:
                siminfo += "\n"+`i` + ":\t%d" % self.__dataSegment.get(i)
            else:
                siminfo += "\t%d" % self.__dataSegment.get(i)

        siminfo += "\n\n"
        print siminfo
        self.__writeSim += siminfo

    def simulator(self):

        self.__pc = self.__codeStart
        cycles = 1

        while(True):

            nowInst = self.__instSegment[self.__pc]
            outputStr = "--------------------\nCycle:%d\t%d\t" % (cycles, self.__pc)
            op = nowInst.replace(",", "").split(" ")
            opname = op[0] + "\t"
            reformInst = nowInst.replace(op[0]+" ",opname)

            outputStr += reformInst
            if nowInst == "BREAK":
                cycles += 1
                self.print_simInfo(outputStr)
                break


            if op[0] in ("ADD","SUB","MUL", "AND","NOR","SLT"):
                self.__pc += self.__instLen
                op1 = int(op[1].replace("R",""))
                op2 = int(op[2].replace("R",""))
                if op[3][0] == '#':
                    op3 = int(op[3].replace("#", ""))
                    self.__regFlie[op1] = MIPS.execute_inst[op[0]](self.__regFlie[op2], op3)
                else:
                    op3 = int(op[3].replace("R", ""))
                    self.__regFlie[op1] = MIPS.execute_inst[op[0]](self.__regFlie[op2], self.__regFlie[op3])


            if op[0] in ("SLL","SRL","SRA"):
                self.__pc += self.__instLen;
                op1 = int(op[1].replace("R",""))
                op2 = int(op[2].replace("R", ""))
                op3 = int(op[3].replace("#", ""))
                self.__regFlie[op1] = MIPS.execute_inst[op[0]](self.__regFlie[op2], op3)

            if op[0] == "J":
                self.__pc += self.__instLen;
                target = int(op[1].replace("#",""))
                self.__pc = target
            if op[0] == "JR":
                self.__pc += self.__instLen;
                op1 = int(op[1].replace("R",""))
                self.__pc =  self.__regFlie[op1]
            if op[0] == "BEQ":
                self.__pc += self.__instLen
                op1 = int(op[1].replace("R",""))
                op2 = int(op[2].replace("R", ""))
                if self.__regFlie[op1] == self.__regFlie[op2]:
                    offset = int(op[3].replace("#", ""))
                    self.__pc += offset

            if op[0] == "BLTZ":
                self.__pc += self.__instLen
                op1 = int(op[1].replace("R", ""))
                if self.__regFlie[op1] < 0:
                    offset = int(op[2].replace("#", ""))
                    self.__pc += offset
            if op[0] == "BGTZ":
                self.__pc += self.__instLen
                op1 = int(op[1].replace("R", ""))
                if self.__regFlie[op1] > 0:
                    offset = int(op[2].replace("#", ""))
                    self.__pc += offset

            if op[0] in ("SW","LW"):
                self.__pc += self.__instLen
                op1 = int(op[1].replace("R", ""))
                num = op[2].split("(")
                offset = int(num[0])
                b = num[1].replace(")", "")
                basereg = int(b.replace("R",""))
                if op[0] == "LW":
                    self.__regFlie[op1] = self.__dataSegment[self.__regFlie[basereg] + offset]
                elif op[0] == "SW":
                    self.__dataSegment[self.__regFlie[basereg] + offset] = self.__regFlie[op1]
            if op[1] == "NOP":
                self.__pc += self.__instLen

            cycles += 1
            self.print_simInfo(outputStr)
        #print self.__writeSim
        self.write_file(self.__writeSim, self.simulationFile)




    #def simulator(self):


if __name__ == '__main__':
    #codeFile = "sample.txt"
    #disassemblyFile = "disassembly.txt"
    #simulationFile = "simulation.txt"
    parser = argparse.ArgumentParser()
    parser.add_argument('testfile', default='sample.txt', help='name of input test file')
    parser.add_argument('--disassemble', '-d', default='disassembly.txt', help='name of output disassembled file')
    parser.add_argument('--simulate', '-s', default='simulation.txt', help='name of output simulated file')
    args = parser.parse_args()


    mips = MIPS(args.testfile,args.disassemble, args.simulate)
    #mips = MIPS(codeFile, disassemblyFile, simulationFile)
    mips.disassemble()
    mips.simulator()
