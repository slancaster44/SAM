program Main;

{$MODE ISO}

{$I Assert.pas}
{$I Arena.pas}
{$I String.pas}
{$I Regex.pas}
{$I Lexer.pas}

var
  testStr : RawString;
  regexArena : pArena;
  testFile : pCharFile;
  lex : pLexer;
  tok : Token;
  i : cardinal;
begin
  testStr := 'Hello';
  regexArena := NewArena();
  Assert(RawStringLength(testStr) = 5);
  Assert(NewString('Hello') = NewString('Hello'));
  Assert(NewString('Hallo') <> NewString('Hello'));
  Assert(RawStringCompare(NewString('Hello')^.contents, 'Hello'));

  testFile := ArenaAllocate(regexArena, sizeof(CharFile));
  assign(testFile^, 'test.txt');
  reset(testFile^);

  lex := NewLexer(regexArena, testFile);

  for i := 0 to 2 do
    begin
      tok := NextToken(lex);

      writeln(tok.content^.contents);
      writeln(cardinal(tok.kind));
      writeln(tok.line);
    end;

  writeln('tests complete');
  DestroyArena(regexArena);
end.
