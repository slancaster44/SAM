
type
  TokenKind = (
    TOK_IDENT, TOK_DOT,
    TOK_COLON, TOK_COMMA, TOK_DASH, TOK_PLUS,
    TOK_HEX_IMM, TOK_BIN_IMM, TOK_DEC_IMM,
    TOK_ZR, TOK_PC, TOK_AC, TOK_IX,
    TOK_SUB, TOK_EOR, TOK_NOR, TOK_ADD, TOK_LD,
    TOK_ST, TOK_SHL, TOK_IN, TOK_OUT,
    TOK_ERROR { Must be at end }
  );

  Token = record
    content : pString;
    kind : TokenKind;
    line : cardinal;
  end;

  Lexer = record
    matchTable : array [TokenKind] of pRegex;
    inputFile : pCharFile;
    curLine : cardinal;
  end;
  pLexer = ^Lexer;

  LexerPosition = record
    line, filePosition : cardinal;
  end;

function NewLexer(a : pArena; inFile : pCharFile) : pLexer;
var
  output : pLexer;
  i : TokenKind;
begin
  output := ArenaAllocate(a, sizeof(Lexer));
  output^.inputFile := inFile;
  output^.curLine := 1;

  output^.matchTable[TOK_IDENT] := CompileRegex(a, '((a-z)|(A-Z))(((A-Z)|(a-z)|(0-9)|(_))*)');
  output^.matchTable[TOK_DOT] := CompileRegex(a, '\.');
  output^.matchTable[TOK_COLON] := CompileRegex(a, ':');
  output^.matchTable[TOK_COMMA] := CompileRegex(a, ',');
  output^.matchTable[TOK_DASH] := CompileRegex(a, '\-');
  output^.matchTable[TOK_PLUS] := CompileRegex(a, '+');
  output^.matchTable[TOK_HEX_IMM] := CompileRegex(a, '0x((0-9)|(a-f)|(A-F))(((0-9)|(a-f)|(A-F))*)');
  output^.matchTable[TOK_BIN_IMM] := CompileRegex(a, '0b(0-1)((0-1)*)');
  output^.matchTable[TOK_DEC_IMM] := CompileRegex(a, '(0-9)((0-9)*)');
  output^.matchTable[TOK_ZR] := CompileRegex(a, '((ZR)|(zr))');
  output^.matchTable[TOK_PC] := CompileRegex(a, '((PC)|(pc))');
  output^.matchTable[TOK_AC] := CompileRegex(a, '((AC)|(ac))');
  output^.matchTable[TOK_IX] := CompileRegex(a, '((IX)|(ix))');
  output^.matchTable[TOK_SUB] := CompileRegex(a, '((SUB)|(sub))');
  output^.matchTable[TOK_EOR] := CompileRegex(a, '((EOR)|(eor)|(XOR)|(xor))');
  output^.matchTable[TOK_NOR] := CompileRegex(a, '((nor)|(NOR))');
  output^.matchTable[TOK_ADD] := CompileRegex(a, '((add)|(ADD))');
  output^.matchTable[TOK_LD] := CompileRegex(a, '((ld)|(LD))');
  output^.matchTable[TOK_ST] := CompileRegex(a, '((st)|(ST))');
  output^.matchTable[TOK_SHL] := CompileRegex(a, '((SHL)|(shl))');
  output^.matchTable[TOK_IN] := CompileRegex(a, '((in)|(IN))');
  output^.matchTable[TOK_OUT] := CompileRegex(a, '((out)|(OUT))');

  for i := TokenKind(0) to TokenKind(cardinal(TOK_ERROR)-1) do
    begin
      Assert(output^.matchTable[i] <> nil);
    end;

  NewLexer := output;
end;

function LexerGetPosition(l : pLexer) : LexerPosition;
var
  output : LexerPosition;
begin
  output.filePosition := filepos(l^.inputFile^);
  output.line := l^.curLine;
  LexerGetPosition := output;
end;

procedure LexerSetPosition(l : pLexer; pos : LexerPosition);
begin
  seek(l^.inputFile^, pos.filePosition);
  l^.curLine := pos.line;
end;

function NextToken(l : pLexer) : Token;
var
  output : Token;
  i : TokenKind;
  content : pString;
  curChar : char;
  pos : cardinal;
begin
  output.kind := TOK_ERROR;
  output.line := l^.curLine;


  if not eof(l^.inputFile^) then
    begin
      read(l^.inputFile^, curChar);
      while ord(curChar) <= 32 do
        begin
          if curChar = chr(10) then l^.curLine := l^.curLine + 1;
          read(l^.inputFile^, curChar);
        end;
      pos := filepos(l^.inputFile^);
      seek(l^.inputFile^, pos-1);
    end;

  for i := TokenKind(0) to TokenKind(cardinal(TOK_ERROR)-1) do
    begin
      content := EvaluateRegexString(l^.matchTable[i], l^.inputFile);
      if content <> nil then 
        begin
          output.kind := i;
          output.content := content;
          break;
        end;
    end;

  NextToken := output;
end;

function PeekToken(l : pLexer) : Token;
var 
  pos : LexerPosition;
  output : Token;
begin
  pos := LexerGetPosition(l);

  output := NextToken(l);

  LexerSetPosition(l, pos);
  PeekToken := output;
end;
