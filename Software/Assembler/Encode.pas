
type
  Instruction = word;
  Opcode = (
    INS_LDIC, INS_LDI, 
    INS_RSVD_0010, INS_RSVD_0011,
    INS_EOR, INS_SUB, INS_NOR,
    INS_ADD, INS_LDAC, INS_STAC,
    INS_LDPC, INS_SHL, INS_IN,
    INS_OUT, INS_RSVD_1111
  );
  Register = (REG_ZR, REG_PC, REG_IX, REG_AC);
  AddressMode = (AM_DIR, AM_DEF, AM_INC, AM_DEC);


function EncodeRRI(op : Opcode; dst, src : Register; imm : word) : Instruction;
var
  op_field, dst_field, src_field : word;
begin
  op_field := (word(op) << 12) and $F000;
  dst_field := (word(dst) << 10) and $0C00;
  src_field := (word(src) << 8) and $0300;
  imm := imm and $00FF;

  EncodeRRI := op_field or dst_field or src_field or imm;
end;


function EncodeARI(op : Opcode; mode : AddressMode; base : Register; imm : word) : Instruction;
var
  op_field, mode_field, base_field : word;
begin
  op_field := (word(op) << 12) and $F000;
  mode_field := (word(mode) << 10) and $0C00;
  base_field := (word(base) << 8) and $0300;
  imm := imm and $00FF;

  EncodeARI := op_field or mode_field or base_field or imm;
end;
