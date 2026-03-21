type
  PassFn = function(lex : pLexer; tok : Token) : boolean;

procedure DoPass(lex : pLexer; pass : PassFn);
var
  tok : Token;
begin
  reset(lex^.inputFile^);

  while not eof(lex^.inputFile^) do
  begin
    tok := NextToken(lex);

    if tok.kind <> TOK_ERROR then
      begin
        if not pass(lex, tok) then exit;
      end
    else if not eof(lex^.inputFile^) then
      begin
        write('line: ');
        writeln(lex^.curLine);
        writeln('unknown token');
        exit;
      end;
  end;
end;
