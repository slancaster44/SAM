#!/usr/bin/python3

# Micro Code Input
# 0-3   Counter
# 4     COUT
# 5-7   N/C
# 8-15  Opcode 

import struct

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
        STEP_11 = 0b1010 << (STEP_OFFSET)
        STEP_12 = 0b1011 << (STEP_OFFSET)
        STEP_13 = 0b1100 << (STEP_OFFSET)
        STEP_14 = 0b1101 << (STEP_OFFSET)
        STEP_16 = 0b1111 << (STEP_OFFSET)

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

    class DestinationRegister:
        ZR = 0b00 << DST_OFFSET
        PC = 0b01 << DST_OFFSET
        IX = 0b10 << DST_OFFSET
        AC = 0b11 << DST_OFFSET

    class AddressingMode:
        DIR = 0b00 << AM_OFFSET
        DEF = 0b01 << AM_OFFSET
        INC = 0b10 << AM_OFFSET
        DEC = 0b11 << AM_OFFSET

    class BaseRegister:
        ZR = 0b00 << BASE_OFFSET
        PC = 0b01 << BASE_OFFSET
        IX = 0b10 << BASE_OFFSET
        AC = 0b11 << BASE_OFFSET

class Outputs:
    ALU_CP_RE = (1 << 0)
    ALU_ROR_HI = (1 << 1)
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
       (0 & SPI_DS_CP_RE) | (SPI_OE_LO) | (0 & SPI_CLK_IN_RE) \
       | (SPI_SH_HI_LD_LO) | (0 & SPI_CLK_IN_RE) | (0 & RST_STEP)
