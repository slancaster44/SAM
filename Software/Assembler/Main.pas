program Main;

{$MODE ISO}

{$I Assert.pas}
{$I Arena.pas}
{$I String.pas}
{$I Regex.pas}
{$I Lexer.pas}
{$I Labels.pas}
{$I PassOne.pas}
{$I Pass.pas}

{$I Parser.pas}
{$I Encode.pas}

var
  lexerArena : pArena;
  testFile : pCharFile;
  lex : pLexer;
begin
  lexerArena := NewArena();
  testFile := ArenaAllocate(lexerArena, sizeof(CharFile));
  assign(testFile^, 'test.txt');

  lex := NewLexer(lexerArena, testFile);

  DoPass(lex, PassOne);

  close(testFile^);
  DestroyArena(lexerArena);
end.
