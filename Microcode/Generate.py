#!/usr/bin/python3

# Micro Code Input
# 0-3   Counter
# 4     COUT
# 5-7   N/C
# 8-15  Opcode 

import struct

OPCODE_OFFSET = 8
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

    class Opcodes:
        ADDI_OP = 0b000 << (5 + OPCODE_OFFSET)
        ADDI_C0 = 0b0 << (4 + OPCODE_OFFSET)
        ADDI_C1 = 0b1 << (4 + OPCODE_OFFSET)
        ADDI_DR_ZR = 0b00 << (2 + OPCODE_OFFSET)
        ADDI_DR_AC = 0b01 << (2 + OPCODE_OFFSET)
        ADDI_DR_IX = 0b10 << (2 + OPCODE_OFFSET)
        ADDI_DR_PC = 0b11 << (2 + OPCODE_OFFSET)
        ADDI_SR_ZR = 0b00 << (OPCODE_OFFSET)
        ADDI_SR_AC = 0b01 << (OPCODE_OFFSET)
        ADDI_SR_IX = 0b10 << (OPCODE_OFFSET)
        ADDI_SR_PC = 0b11 << (OPCODE_OFFSET)

class Outputs:
    # Arithmetic & Logical Unit
    ALU_CP_RE = 1 << 0
    ALU_OE_LO = 1 << 1
    ALU_FN_SEL_0 = 1 << 2
    ALU_FN_SEL_1 = 1 << 3
    ALU_COUT_CP_RE = 1 << 4

    # Right Hand Side Bus
    RHS_ZR_OE_LO = 1 << 5
    MOR_CP_RE = 1 << 6
    MOR_OE_LO = 1 << 7
    IR_CP_RE = 1 << 8
    IMM_OE_LO = 1 << 9
    
    # Memory
    MEM_WE_HI = 1 << 10
    MEM_IN_SEL = 1 << 11
    MEM_WR_RE = 1 << 12
    MAR_CP_RE = 1 << 24
    MAR_OE_LO = 1 << 25

    # Left hand side bus
    LHS_ZR_OE_LO = 1 << 13
    AC_CP_RE = 1 << 14
    AC_CP_OE_LO = 1 << 15
    IX_CP_RE = 1 << 16
    IX_OE_LO = 1 << 17
    PC_CP_FE = 1 << 18
    PC_CEP_HI = 1 << 19
    PC_OE_LO = 1 << 23

    # SPI
    SCLK = 1 << 20
    DS_CP_RE = 1 << 26
    SPI_OE_LO = 1 << 27
    SPI_CLK_IN_RE = 1 << 28
    SPI_SH_HI_LD_LO = 1 << 29
    SPI_CLK_OUT_RE = 1 << 30

    # Control
    STEP_RST_LO = 1 << 31

    DEFAULT_OUTPUTS = \
        (0 & ALU_CP_RE) | (ALU_OE_LO) | (0 & ALU_FN_SEL_0) | \
        (0 & ALU_FN_SEL_1) | (0 & ALU_COUT_CP_RE) | (RHS_ZR_OE_LO) | \
        (0 & MOR_CP_RE) | (MOR_OE_LO) | (0 & IR_CP_RE) | \
        (IMM_OE_LO) | (0 & MEM_WE_HI) | (0 & MEM_IN_SEL) | \
        (0 & MEM_WR_RE) | (0 & MAR_CP_RE) | (MAR_OE_LO) | \
        (LHS_ZR_OE_LO) | (0 & AC_CP_RE) | (AC_CP_OE_LO) | \
        (0 & IX_CP_RE) | (IX_OE_LO) | (PC_CP_FE) | \
        (0 & PC_CEP_HI) | (PC_OE_LO) | (0 & SCLK) | \
        (0 & DS_CP_RE) | (SPI_OE_LO) | (0 & SPI_CLK_IN_RE) | \
        (SPI_SH_HI_LD_LO) | (0 & SPI_CLK_OUT_RE) | (STEP_RST_LO) 


def DoInsertLDI(sr, dr, cond, microcode: list[int]) -> list[int]:
    for actual in [Inputs.State.COUT_0, Inputs.State.COUT_1]:
        opcode = Inputs.Opcodes.ADDI_OP | cond | sr | dr

        source_signal = 0
        if sr == Inputs.Opcodes.ADDI_SR_ZR:
            source_signal = ~Outputs.LHS_ZR_OE_LO
        elif sr == Inputs.Opcodes.ADDI_SR_AC:
            source_signal = ~Outputs.AC_CP_OE_LO
        elif sr == Inputs.Opcodes.ADDI_SR_IX:
            source_signal = ~Outputs.IX_OE_LO
        elif sr == Inputs.Opcodes.ADDI_SR_PC:
            source_signal = ~Outputs.PC_OE_LO
        else:
            raise RuntimeError("Unknown source register")
        
        dest_signal = 0
        if dr == Inputs.Opcodes.ADDI_DR_ZR:
            return microcode #Some type of nop
        elif dr == Inputs.Opcodes.ADDI_DR_AC:
            dest_signal = Outputs.AC_CP_RE
        elif dr == Inputs.Opcodes.ADDI_DR_IX:
            dest_signal = Outputs.IX_CP_RE
        elif dr == Inputs.Opcodes.ADDI_DR_PC:
            dest_signal = ~Outputs.PC_CP_FE

        step2 = Outputs.DEFAULT_OUTPUTS
        step2 &= source_signal
        step2 &= ~Outputs.IMM_OE_LO
        step2 &= ~Outputs.ALU_FN_SEL_0
        step2 &= ~Outputs.ALU_FN_SEL_1

        step3 = step2
        step3 |= Outputs.ALU_CP_RE
        step3 &= ~Outputs.ALU_OE_LO

        step4 = Outputs.DEFAULT_OUTPUTS
        step4 &= ~Outputs.ALU_OE_LO
        if dr == Inputs.Opcodes.ADDI_DR_PC:
            step4 &= dest_signal
        else:
            step4 |= dest_signal
        step4 &= ~Outputs.STEP_RST_LO

        if (actual == Inputs.State.COUT_0 and cond == Inputs.Opcodes.ADDI_C1):
            step2 = Outputs.DEFAULT_OUTPUTS
            step2 &= ~Outputs.MEM_IN_SEL
            step2 |= Outputs.PC_CEP_HI
            step2 |= Outputs.IR_CP_RE

            step3 = Outputs.DEFAULT_OUTPUTS
            step3 |= Outputs.PC_CEP_HI
            step3 &= ~Outputs.PC_CP_FE

            step4 = Outputs.DEFAULT_OUTPUTS
            
        microcode [
            opcode | 
            actual | 
            Inputs.State.STEP_2
        ] = step2
        microcode [
            opcode | 
            actual | 
            Inputs.State.STEP_3
        ] = step3
        microcode [
            opcode | 
            actual | 
            Inputs.State.STEP_3
        ] = step3
        microcode [
            opcode | 
            actual | 
            Inputs.State.STEP_4
        ] = step4

    return microcode

def InsertLoadImmediate(microcode: list[int]) -> list[int]:
    for sr in [
        Inputs.Opcodes.ADDI_SR_ZR, 
        Inputs.Opcodes.ADDI_SR_AC, 
        Inputs.Opcodes.ADDI_SR_IX, 
        Inputs.Opcodes.ADDI_SR_PC
    ]:
        for dr in [
            Inputs.Opcodes.ADDI_DR_ZR,
            Inputs.Opcodes.ADDI_DR_AC,
            Inputs.Opcodes.ADDI_DR_IX,
            Inputs.Opcodes.ADDI_DR_PC,
        ]:
            microcode = DoInsertLDI(sr, dr, Inputs.Opcodes.ADDI_C0, microcode)
            microcode = DoInsertLDI(sr, dr, Inputs.Opcodes.ADDI_C1, microcode)

    return microcode

def InsertFetch(opcode : int, microcode: list[int]) -> list[int]:
    # Because MEM_IN_SEL is default to zero, we should already be ready
    step0 = Outputs.DEFAULT_OUTPUTS
    step0 &= ~Outputs.MEM_IN_SEL
    step0 |= Outputs.PC_CEP_HI
    step0 |= Outputs.IR_CP_RE

    step1 = Outputs.DEFAULT_OUTPUTS
    step1 |= Outputs.PC_CEP_HI
    step1 &= ~Outputs.PC_CP_FE

    microcode [
        opcode | 
        Inputs.State.COUT_0 | 
        Inputs.State.STEP_0
    ] = step0
    microcode [
        opcode | 
        Inputs.State.COUT_1 | 
        Inputs.State.STEP_0
    ] = step0

    microcode [
        opcode | 
        Inputs.State.COUT_0 | 
        Inputs.State.STEP_1
    ] = step1
    microcode [
        opcode | 
        Inputs.State.COUT_1 | 
        Inputs.State.STEP_1
    ] = step1

    return microcode

MicroCodeGenerators = [InsertLoadImmediate]

if __name__ == '__main__':
    output = [Outputs.DEFAULT_OUTPUTS for _ in range((2 ** 16))]
    for i in range(256):
        output = InsertFetch(i << OPCODE_OFFSET, output)

    for fn in MicroCodeGenerators:
        output = fn(output)

    with open("microcode.bin", "wb") as f:                
        for word in output:
            outbytes = struct.pack(">L", word)
            f.write(outbytes)

    with open("test.bin", "wb") as f:
        for idx in range((2 ** 16)-1):
            out = 0x0400 | (idx+0xFF & 0xFF)
            outbytes = struct.pack(">H", out)
            f.write(outbytes)
