#!/usr/bin/python3

# Micro Code Input
# 0-3   Counter
# 4     COUT
# 5-7   N/C
# 8-15  Opcode 

import struct
import itertools

OPCODE_OFFSET = 12
DST_OFFSET = 10
SRC_OFFSET = 8
AM_OFFSET = 10
BASE_OFFSET = 8

COUT_OFFSET = 4
STEP_OFFSET = 0

class Inputs:
    class State:
        COUT_0 = 0b0 << (COUT_OFFSET)
        COUT_1 = 0b1 << (COUT_OFFSET)
        ALL_CONDS = [COUT_0, COUT_1]

        STEP_0  = 0b0000 << (STEP_OFFSET)
        STEP_1 = 0b0001 << (STEP_OFFSET)
        STEP_2 = 0b0010 << (STEP_OFFSET)
        STEP_3 = 0b0011 << (STEP_OFFSET)
        STEP_4 = 0b0100 << (STEP_OFFSET)
        STEP_5 = 0b0101 << (STEP_OFFSET)
        STEP_6 = 0b0110 << (STEP_OFFSET)
        STEP_7 = 0b0111 << (STEP_OFFSET)
        STEP_8 = 0b1000 << (STEP_OFFSET)
        STEP_9 = 0b1001 << (STEP_OFFSET)
        STEP_10 = 0b1010 << (STEP_OFFSET)
        STEP_11 = 0b1011 << (STEP_OFFSET)
        STEP_12 = 0b1100 << (STEP_OFFSET)
        STEP_13 = 0b1101 << (STEP_OFFSET)
        STEP_14 = 0b1110 << (STEP_OFFSET)
        STEP_15 = 0b1111 << (STEP_OFFSET)

    class Opcode:
        SUBIC = 0b0000 << OPCODE_OFFSET 
        SUBI = 0b0001 << OPCODE_OFFSET
        EOR = 0b0100 << OPCODE_OFFSET
        SUB = 0b0101 << OPCODE_OFFSET
        NOR = 0b0110 << OPCODE_OFFSET
        ADD = 0b0111 << OPCODE_OFFSET
        LD = 0b1000 << OPCODE_OFFSET
        ST = 0b1001 << OPCODE_OFFSET
        ROR = 0b1010 << OPCODE_OFFSET
        SHL = 0b1011 << OPCODE_OFFSET
        IN = 0b1100 << OPCODE_OFFSET
        OUT = 0b1101 << OPCODE_OFFSET

    class SourceRegister:
        ZR = 0b00 << SRC_OFFSET
        PC = 0b01 << SRC_OFFSET
        IX = 0b10 << SRC_OFFSET
        AC = 0b11 << SRC_OFFSET
        ALL = [ZR, PC, IX, AC]

    class DestinationRegister:
        ZR = 0b00 << DST_OFFSET
        PC = 0b01 << DST_OFFSET
        IX = 0b10 << DST_OFFSET
        AC = 0b11 << DST_OFFSET
        ALL = [ZR, PC, IX, AC]

    class AddressingMode:
        DIR = 0b00 << AM_OFFSET
        DEF = 0b01 << AM_OFFSET
        INC = 0b10 << AM_OFFSET
        DEC = 0b11 << AM_OFFSET
        ALL = [DIR, DEF, INC, DEC]

    class BaseRegister:
        ZR = 0b00 << BASE_OFFSET
        PC = 0b01 << BASE_OFFSET
        IX = 0b10 << BASE_OFFSET
        AC = 0b11 << BASE_OFFSET
        ALL = [ZR, PC, IX, AC]

class Outputs:
    ALU_CP_RE = (1 << 0)
    ALU_FN_SEL_0 = (1 << 2)
    ALU_FN_SEL_1 = (1 << 3)
    ALU_COUT_CP_RE = (1 << 4)

    RHS_ZR_OE_LO = (1 << 5)
    MOR_CP_RE = (1 << 6)
    MOR_OE_LO = (1 << 7)
    IR_CP_RE = (1 << 8)
    IR_IMM_OE_LO = (1 << 9)
    MEM_WE_HI = (1 << 10)
    MEM_IN_SEL = (1 << 11)
    MEM_CP_WR_RE = (1 << 12)

    LHS_IMM_0 = (1 << 13)
    LHS_IMM_S = (1 << 14)
    LHS_IMM_OE_LO = (1 << 15)
    AC_CP_RE = (1 << 16)
    AC_OE_LO = (1 << 17)
    IX_CP_RE = (1 << 18)
    IX_OE_LO = (1 << 19)
    PC_CP_FE = (1 << 20)
    PC_CEP_HI = (1 << 21)
    
    SCLK = (1 << 22)
    PC_YB_OE_LO = (1 << 23)
    MAR_CP_RE = (1 << 24)
    MAR_OE_LO = (1 << 25)
    SPI_DS_CP_RE = (1 << 26)
    SPI_OE_LO = (1 << 27)
    SPI_CLK_IN_RE = (1 << 28)
    SPI_SH_HI_LD_LO = (1 << 29)
    SPI_CLK_OUT_RE = (1 << 30)

    RST_STEP = (1 << 31)

    DEFAULT_OUTPUT = \
        (0 & ALU_CP_RE) | (0 & ALU_FN_SEL_0) | (0 & ALU_FN_SEL_1) | (0 & ALU_COUT_CP_RE ) \
        | (MOR_OE_LO) | (0 & MOR_CP_RE) | (RHS_ZR_OE_LO) \
        | (0 & MEM_WE_HI) | (IR_IMM_OE_LO) | (0 & IR_CP_RE) \
        | (0 & LHS_IMM_0) | (0 & MEM_CP_WR_RE) | (0 & MEM_IN_SEL) \
        | (0 & AC_CP_RE) | (LHS_IMM_OE_LO) | (0 & LHS_IMM_S) \
        | (IX_OE_LO) | (0 & IX_CP_RE) | (AC_OE_LO) \
        | (0 & SCLK) | (PC_CEP_HI) | (PC_CP_FE) \
        | (PC_YB_OE_LO) | (0 & MAR_CP_RE) | (MAR_OE_LO) \
        | (0 & SPI_DS_CP_RE) | (SPI_OE_LO) | (0 & SPI_CLK_IN_RE) \
        | (SPI_SH_HI_LD_LO) | (0 & SPI_CLK_IN_RE) | (RST_STEP)

class MicrocodeBuilders:
    def __init__(self):
        self.builders = [
            self.placeFetches, 
            self.placeSubtractImmediate,
            self.placeDirectMemoryMath,
            self.placeDeferredMemoryMath,
            self.placeIncMemoryMath,
            self.placeDecMemoryMath,
        ]

    def ApplyBuilders(self, microcode):
        [x(microcode) for x in self.builders]

    def placeFetches(self, microcode):
        for i in range(256):
            step0_c0_location = (i << BASE_OFFSET) | Inputs.State.STEP_0 | Inputs.State.COUT_0
            step0_c1_location = (i << BASE_OFFSET) | Inputs.State.STEP_0 | Inputs.State.COUT_1

            step1_c0_location = (i << BASE_OFFSET) | Inputs.State.STEP_1 | Inputs.State.COUT_0
            step1_c1_location = (i << BASE_OFFSET) | Inputs.State.STEP_1 | Inputs.State.COUT_1

            microcode[step0_c0_location] = Outputs.DEFAULT_OUTPUT | Outputs.IR_CP_RE
            microcode[step0_c1_location] = Outputs.DEFAULT_OUTPUT | Outputs.IR_CP_RE

            microcode[step1_c0_location] = Outputs.DEFAULT_OUTPUT & (~Outputs.PC_CP_FE)
            microcode[step1_c1_location] = Outputs.DEFAULT_OUTPUT & (~Outputs.PC_CP_FE)

    def placeSubtractImmediate(self, microcode):
        options = itertools.product(
            [Inputs.Opcode.SUBI, Inputs.Opcode.SUBIC],
            Inputs.DestinationRegister.ALL,
            Inputs.SourceRegister.ALL,
            Inputs.State.ALL_CONDS)

        for (op, dr, sr, cond) in options:
            opcode = op | dr | sr | cond 

            step0_code = opcode | Inputs.State.STEP_1
            step1_code = opcode | Inputs.State.STEP_2
            step2_code = opcode | Inputs.State.STEP_3

            if (cond == Inputs.State.COUT_0) and (op == Inputs.Opcode.SUBIC):
                microcode[step0_code] &= ~(Outputs.RST_STEP)
                continue

            sr_signal = 0
            if sr == Inputs.SourceRegister.AC:
                sr_signal = Outputs.AC_OE_LO
            elif sr == Inputs.SourceRegister.IX:
                sr_signal = Outputs.IX_OE_LO
            elif sr == Inputs.SourceRegister.PC:
                sr_signal = Outputs.PC_YB_OE_LO
            elif sr == Inputs.SourceRegister.ZR:
                sr_signal = Outputs.LHS_IMM_OE_LO
            else:
                raise RuntimeError("unhandled source register")

            dr_signal = 0
            if dr == Inputs.DestinationRegister.AC:
                dr_signal = Outputs.AC_CP_RE
            elif dr == Inputs.DestinationRegister.IX:
                dr_signal = Outputs.IX_CP_RE
            elif dr == Inputs.DestinationRegister.PC:
                dr_signal = Outputs.PC_CP_FE | Outputs.PC_CEP_HI
            elif dr == Inputs.DestinationRegister.ZR:
                dr_signal = 0
            else:
                raise RuntimeError("unhandled destination register")

            microcode[step0_code] &= (~sr_signal) 
            microcode[step0_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step0_code] |= Outputs.ALU_FN_SEL_1
            
            microcode[step1_code] &= (~sr_signal) 
            microcode[step1_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step1_code] |= Outputs.ALU_FN_SEL_1
            microcode[step1_code] |= Outputs.ALU_CP_RE 
            microcode[step1_code] |= Outputs.ALU_COUT_CP_RE
            
            microcode[step2_code] |= (dr_signal)
            microcode[step2_code] &= (~Outputs.RST_STEP)
                
            if dr == Inputs.DestinationRegister.PC:
                microcode[step2_code] &= (~dr_signal)
                microcode[step2_code] &= (~Outputs.RST_STEP)

    def placeDirectMemoryMath(self, microcode):
        options = itertools.product(
            [Inputs.Opcode.ADD, Inputs.Opcode.SUB, Inputs.Opcode.EOR, Inputs.Opcode.NOR, Inputs.Opcode.LD],
            Inputs.BaseRegister.ALL,
            Inputs.State.ALL_CONDS)
        
        for (op, base, cond) in options:
            opcode = op | Inputs.AddressingMode.DIR | base | cond

            step0_code = opcode | Inputs.State.STEP_1
            step1_code = opcode | Inputs.State.STEP_2
            step2_code = opcode | Inputs.State.STEP_3
            step3_code = opcode | Inputs.State.STEP_4
            step4_code = opcode | Inputs.State.STEP_5
            step5_code = opcode | Inputs.State.STEP_6

            base_signal = 0
            if base == Inputs.BaseRegister.AC:
                base_signal = Outputs.AC_OE_LO
            elif base == Inputs.BaseRegister.IX:
                base_signal = Outputs.IX_OE_LO
            elif base == Inputs.BaseRegister.PC:
                base_signal = Outputs.PC_YB_OE_LO
            elif base == Inputs.BaseRegister.ZR:
                base_signal = Outputs.LHS_IMM_OE_LO
            else:
                raise RuntimeError("unhandled base register")
            
            arith_op = 0
            if op == Inputs.Opcode.ADD or op == Inputs.Opcode.LD:
                arith_op = 0
            elif op == Inputs.Opcode.SUB:
                arith_op = Outputs.ALU_FN_SEL_0
            elif op == Inputs.Opcode.NOR:
                arith_op = Outputs.ALU_FN_SEL_1
            elif op == Inputs.Opcode.EOR:
                arith_op = Outputs.ALU_FN_SEL_0 | Outputs.ALU_FN_SEL_1
            else:
                raise RuntimeError("unhandled direct memory operation")

            microcode[step0_code] &= (~base_signal) 
            microcode[step0_code] &= (~Outputs.IR_IMM_OE_LO) 

            microcode[step1_code] &= (~base_signal) 
            microcode[step1_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step1_code] |= Outputs.ALU_CP_RE 

            microcode[step2_code] |= Outputs.MAR_CP_RE
            microcode[step2_code] &= (~Outputs.MAR_OE_LO)
            microcode[step2_code] |= Outputs.MEM_IN_SEL

            microcode[step3_code] &= (~Outputs.MAR_OE_LO)
            microcode[step3_code] |= Outputs.MEM_IN_SEL
            microcode[step3_code] |= Outputs.MOR_CP_RE
            microcode[step3_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step3_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step3_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step3_code] |= arith_op

            microcode[step4_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step4_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step4_code] &= (~Outputs.LHS_IMM_OE_LO)

            microcode[step4_code] |= arith_op
            microcode[step4_code] |= Outputs.ALU_COUT_CP_RE
            microcode[step4_code] |= Outputs.ALU_CP_RE

            microcode[step5_code] |= Outputs.AC_CP_RE
            microcode[step5_code] &= (~Outputs.RST_STEP)

    def placeDeferredMemoryMath(self, microcode):
        options = itertools.product(
            [Inputs.Opcode.ADD, Inputs.Opcode.SUB, Inputs.Opcode.EOR, Inputs.Opcode.NOR, Inputs.Opcode.LD],
            Inputs.BaseRegister.ALL,
            Inputs.State.ALL_CONDS)
        
        for (op, base, cond) in options:
            opcode = op | Inputs.AddressingMode.DEF | base | cond

            step0_code = opcode | Inputs.State.STEP_1
            step1_code = opcode | Inputs.State.STEP_2
            step2_code = opcode | Inputs.State.STEP_3
            step3_code = opcode | Inputs.State.STEP_4
            step4_code = opcode | Inputs.State.STEP_5
            step5_code = opcode | Inputs.State.STEP_6
            step6_code = opcode | Inputs.State.STEP_7
            step7_code = opcode | Inputs.State.STEP_8
            step8_code = opcode | Inputs.State.STEP_9

            base_signal = 0
            if base == Inputs.BaseRegister.AC:
                base_signal = Outputs.AC_OE_LO
            elif base == Inputs.BaseRegister.IX:
                base_signal = Outputs.IX_OE_LO
            elif base == Inputs.BaseRegister.PC:
                base_signal = Outputs.PC_YB_OE_LO
            elif base == Inputs.BaseRegister.ZR:
                base_signal = Outputs.LHS_IMM_OE_LO
            else:
                raise RuntimeError("unhandled base register")
            
            arith_op = 0
            if op == Inputs.Opcode.ADD or op == Inputs.Opcode.LD:
                arith_op = 0
            elif op == Inputs.Opcode.SUB:
                arith_op = Outputs.ALU_FN_SEL_0
            elif op == Inputs.Opcode.NOR:
                arith_op = Outputs.ALU_FN_SEL_1
            elif op == Inputs.Opcode.EOR:
                arith_op = Outputs.ALU_FN_SEL_0 | Outputs.ALU_FN_SEL_1
            else:
                raise RuntimeError("unhandled direct memory operation")

            microcode[step0_code] &= (~base_signal) 
            microcode[step0_code] &= (~Outputs.IR_IMM_OE_LO) 

            microcode[step1_code] &= (~base_signal) 
            microcode[step1_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step1_code] |= Outputs.ALU_CP_RE 

            microcode[step2_code] |= Outputs.MAR_CP_RE
            microcode[step2_code] &= (~Outputs.MAR_OE_LO)
            microcode[step2_code] |= Outputs.MEM_IN_SEL

            microcode[step3_code] &= (~Outputs.MAR_OE_LO)
            microcode[step3_code] |= Outputs.MEM_IN_SEL
            microcode[step3_code] |= Outputs.MOR_CP_RE
            microcode[step3_code] &= (~Outputs.MOR_OE_LO)
            microcode[step3_code] &= (~Outputs.LHS_IMM_OE_LO)

            microcode[step4_code] &= (~Outputs.MOR_OE_LO)
            microcode[step4_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step4_code] |= Outputs.ALU_CP_RE

            microcode[step5_code] |= Outputs.MAR_CP_RE
            microcode[step5_code] &= (~Outputs.MAR_OE_LO)
            microcode[step5_code] |= Outputs.MEM_IN_SEL

            microcode[step6_code] &= (~Outputs.MAR_OE_LO)
            microcode[step6_code] |= Outputs.MEM_IN_SEL
            microcode[step6_code] |= Outputs.MOR_CP_RE
            microcode[step6_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step6_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step6_code] &= (~Outputs.AC_OE_LO)
            microcode[step6_code] |= arith_op

            microcode[step7_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step7_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step7_code] &= (~Outputs.LHS_IMM_OE_LO)

            microcode[step7_code] |= arith_op
            microcode[step7_code] |= Outputs.ALU_COUT_CP_RE
            microcode[step7_code] |= Outputs.ALU_CP_RE

            microcode[step8_code] |= Outputs.AC_CP_RE
            microcode[step8_code] &= (~Outputs.RST_STEP)

    def placeIncMemoryMath(self, microcode):
        options = itertools.product(
            [Inputs.Opcode.ADD, Inputs.Opcode.SUB, Inputs.Opcode.EOR, Inputs.Opcode.NOR, Inputs.Opcode.LD],
            Inputs.BaseRegister.ALL,
            Inputs.State.ALL_CONDS)
        
        for (op, base, cond) in options:
            opcode = op | Inputs.AddressingMode.INC | base | cond

            step0_code = opcode | Inputs.State.STEP_1
            step1_code = opcode | Inputs.State.STEP_2
            step2_code = opcode | Inputs.State.STEP_3
            step3_code = opcode | Inputs.State.STEP_4
            step4_code = opcode | Inputs.State.STEP_5
            step5_code = opcode | Inputs.State.STEP_6
            step6_code = opcode | Inputs.State.STEP_7
            step7_code = opcode | Inputs.State.STEP_8
            step8_code = opcode | Inputs.State.STEP_9
            step9_code = opcode | Inputs.State.STEP_10

            base_signal = 0
            if base == Inputs.BaseRegister.AC:
                base_signal = Outputs.AC_OE_LO
            elif base == Inputs.BaseRegister.IX:
                base_signal = Outputs.IX_OE_LO
            elif base == Inputs.BaseRegister.PC:
                base_signal = Outputs.PC_YB_OE_LO
            elif base == Inputs.BaseRegister.ZR:
                base_signal = Outputs.LHS_IMM_OE_LO
            else:
                raise RuntimeError("unhandled base register")
            
            arith_op = 0
            if op == Inputs.Opcode.ADD or op == Inputs.Opcode.LD:
                arith_op = 0
            elif op == Inputs.Opcode.SUB:
                arith_op = Outputs.ALU_FN_SEL_0
            elif op == Inputs.Opcode.NOR:
                arith_op = Outputs.ALU_FN_SEL_1
            elif op == Inputs.Opcode.EOR:
                arith_op = Outputs.ALU_FN_SEL_0 | Outputs.ALU_FN_SEL_1
            else:
                raise RuntimeError("unhandled direct memory operation")

            microcode[step0_code] &= (~base_signal) 
            microcode[step0_code] &= (~Outputs.IR_IMM_OE_LO) 

            microcode[step1_code] &= (~base_signal) 
            microcode[step1_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step1_code] |= Outputs.ALU_CP_RE 

            microcode[step2_code] |= Outputs.MAR_CP_RE
            microcode[step2_code] &= (~Outputs.MAR_OE_LO)
            microcode[step2_code] |= Outputs.MEM_IN_SEL

            microcode[step3_code] &= (~Outputs.MAR_OE_LO)
            microcode[step3_code] |= Outputs.MEM_IN_SEL
            microcode[step3_code] |= Outputs.MOR_CP_RE
            microcode[step3_code] &= (~Outputs.MOR_OE_LO)
            microcode[step3_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step3_code] |= Outputs.LHS_IMM_0

            microcode[step4_code] &= (~Outputs.MOR_OE_LO)
            microcode[step4_code] |= Outputs.LHS_IMM_0
            microcode[step4_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step4_code] |= Outputs.ALU_CP_RE
            microcode[step4_code] |= Outputs.MEM_WE_HI
            microcode[step4_code] |= Outputs.MEM_IN_SEL
            microcode[step4_code] &= (~Outputs.MAR_OE_LO)

            microcode[step5_code] |= Outputs.MEM_WE_HI
            microcode[step5_code] |= Outputs.MEM_IN_SEL
            microcode[step5_code] |= Outputs.MEM_CP_WR_RE
            microcode[step5_code] &= (~Outputs.MAR_OE_LO)

            microcode[step6_code] |= Outputs.MAR_CP_RE
            microcode[step6_code] &= (~Outputs.MAR_OE_LO)
            microcode[step6_code] |= Outputs.MEM_IN_SEL

            microcode[step7_code] &= (~Outputs.MAR_OE_LO)
            microcode[step7_code] |= Outputs.MEM_IN_SEL
            microcode[step7_code] |= Outputs.MOR_CP_RE
            microcode[step7_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step7_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step7_code] &= (~Outputs.AC_OE_LO)
            microcode[step7_code] |= arith_op

            microcode[step8_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step8_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step8_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step8_code] |= arith_op
            microcode[step8_code] |= Outputs.ALU_COUT_CP_RE
            microcode[step8_code] |= Outputs.ALU_CP_RE

            microcode[step9_code] |= Outputs.AC_CP_RE
            microcode[step9_code] &= (~Outputs.RST_STEP)


    def placeDecMemoryMath(self, microcode):
        options = itertools.product(
            [Inputs.Opcode.ADD, Inputs.Opcode.SUB, Inputs.Opcode.EOR, Inputs.Opcode.NOR, Inputs.Opcode.LD],
            Inputs.BaseRegister.ALL,
            Inputs.State.ALL_CONDS)
        
        for (op, base, cond) in options:
            opcode = op | Inputs.AddressingMode.DEC | base | cond

            step0_code = opcode | Inputs.State.STEP_1
            step1_code = opcode | Inputs.State.STEP_2
            step2_code = opcode | Inputs.State.STEP_3
            step3_code = opcode | Inputs.State.STEP_4
            step4_code = opcode | Inputs.State.STEP_5
            step5_code = opcode | Inputs.State.STEP_6
            step6_code = opcode | Inputs.State.STEP_7
            step7_code = opcode | Inputs.State.STEP_8
            step8_code = opcode | Inputs.State.STEP_9
            step9_code = opcode | Inputs.State.STEP_10
            step10_code = opcode | Inputs.State.STEP_11

            base_signal = 0
            if base == Inputs.BaseRegister.AC:
                base_signal = Outputs.AC_OE_LO
            elif base == Inputs.BaseRegister.IX:
                base_signal = Outputs.IX_OE_LO
            elif base == Inputs.BaseRegister.PC:
                base_signal = Outputs.PC_YB_OE_LO
            elif base == Inputs.BaseRegister.ZR:
                base_signal = Outputs.LHS_IMM_OE_LO
            else:
                raise RuntimeError("unhandled base register")
            
            arith_op = 0
            if op == Inputs.Opcode.ADD or op == Inputs.Opcode.LD:
                arith_op = 0
            elif op == Inputs.Opcode.SUB:
                arith_op = Outputs.ALU_FN_SEL_0
            elif op == Inputs.Opcode.NOR:
                arith_op = Outputs.ALU_FN_SEL_1
            elif op == Inputs.Opcode.EOR:
                arith_op = Outputs.ALU_FN_SEL_0 | Outputs.ALU_FN_SEL_1
            else:
                raise RuntimeError("unhandled direct memory operation")

            microcode[step0_code] &= (~base_signal) 
            microcode[step0_code] &= (~Outputs.IR_IMM_OE_LO) 

            microcode[step1_code] &= (~base_signal) 
            microcode[step1_code] &= (~Outputs.IR_IMM_OE_LO) 
            microcode[step1_code] |= Outputs.ALU_CP_RE 

            microcode[step2_code] |= Outputs.MAR_CP_RE
            microcode[step2_code] &= (~Outputs.MAR_OE_LO)
            microcode[step2_code] |= Outputs.MEM_IN_SEL

            microcode[step3_code] &= (~Outputs.MAR_OE_LO)
            microcode[step3_code] |= Outputs.MEM_IN_SEL
            microcode[step3_code] |= Outputs.MOR_CP_RE
            microcode[step3_code] &= (~Outputs.MOR_OE_LO)
            microcode[step3_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step3_code] |= Outputs.LHS_IMM_0
            microcode[step3_code] |= Outputs.LHS_IMM_S

            microcode[step4_code] &= (~Outputs.MOR_OE_LO)
            microcode[step4_code] |= Outputs.LHS_IMM_0
            microcode[step3_code] |= Outputs.LHS_IMM_S
            microcode[step4_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step4_code] |= Outputs.ALU_CP_RE
            microcode[step4_code] |= Outputs.MEM_WE_HI
            microcode[step4_code] |= Outputs.MEM_IN_SEL
            microcode[step4_code] &= (~Outputs.MAR_OE_LO)

            microcode[step5_code] |= Outputs.MEM_WE_HI
            microcode[step5_code] |= Outputs.MEM_IN_SEL
            microcode[step5_code] |= Outputs.MEM_CP_WR_RE
            microcode[step5_code] &= (~Outputs.MAR_OE_LO)

            microcode[step5_code] &= (~Outputs.MOR_OE_LO)
            microcode[step5_code] &= (~Outputs.LHS_IMM_OE_LO)

            microcode[step6_code] &= (~Outputs.MOR_OE_LO)
            microcode[step6_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step6_code] |= Outputs.ALU_CP_RE

            microcode[step7_code] |= Outputs.MAR_CP_RE
            microcode[step7_code] &= (~Outputs.MAR_OE_LO)
            microcode[step7_code] |= Outputs.MEM_IN_SEL

            microcode[step8_code] &= (~Outputs.MAR_OE_LO)
            microcode[step8_code] |= Outputs.MEM_IN_SEL
            microcode[step8_code] |= Outputs.MOR_CP_RE
            microcode[step8_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step8_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step8_code] &= (~Outputs.AC_OE_LO)
            microcode[step8_code] |= arith_op

            microcode[step9_code] &= (~Outputs.MOR_OE_LO)
            if op != Inputs.Opcode.LD: 
                microcode[step9_code] &= (~Outputs.AC_OE_LO)
            else:
                microcode[step9_code] &= (~Outputs.LHS_IMM_OE_LO)
            microcode[step9_code] |= arith_op
            microcode[step9_code] |= Outputs.ALU_COUT_CP_RE
            microcode[step9_code] |= Outputs.ALU_CP_RE

            microcode[step10_code] |= Outputs.AC_CP_RE
            microcode[step10_code] &= (~Outputs.RST_STEP)

if __name__ == '__main__':
    output = [Outputs.DEFAULT_OUTPUT] * (2 ** 16)
    builders = MicrocodeBuilders()
    builders.ApplyBuilders(output)

    out_file = open('microcode.bin', 'wb')

    for word in output:
        micro_word = struct.pack(">L", word)
        out_file.write(micro_word)

    out_file.close()

    out_file = open('test.bin', 'wb')
    outputs = [0b0111_11_00_11111111 | (0xFF & (i+0xA5)) for i in range(255)] + [0xA5 for i in range((2 ** 16) - 255)]
    outputs = [struct.pack(">H", x) for x in outputs]
    [out_file.write(x) for x in outputs]
