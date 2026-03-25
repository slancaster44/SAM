
type
  SyntaxTree = record
    child : ^SyntaxTree;
    tok : Token;
  end;
  pSyntaxTree = ^SyntaxTree;

  SyntaxRule = record
    next : ^SyntaxRule;
    match : TokenKind;
  end;
  pSyntaxRule = ^SyntaxRule;

  RuleList = record
    next : ^RuleList;
    rule : SyntaxRule;
  end;
  pRuleList = ^RuleList;

  Parser = record
    lex : pLexer;
    stmtArena : pArena;
    rules : pRuleList;
  end;
  pParser = ^Parser;

function AppendRule(a : pArena; kind : TokenKind; head : pSyntaxRule) : pSyntaxRule;
var
  newRule : pSyntaxRule;
begin
  newRule := ArenaAllocate(a, sizeof(SyntaxRule));
  newRule^.next := nil;
  newRule^.match := kind;

  if head = nil then
    begin
      AppendRule := newRule;
    end
  else
    begin
      while (head^.next <> nil) do
        head := head^.next;
      
      head^.next := newRule;
      AppendRule := newRule;
    end;

end;

function SyntaxMatch(a : pArena; lexer : pLexer; rule : pSyntaxRule) : pSyntaxTree;
var
  tok : Token;
  output : pSyntaxTree;
begin
  output := nil;
  tok := NextToken(lexer);
  if tok.kind = rule^.match then
    begin
      output := ArenaAllocate(a, sizeof(SyntaxTree));
      output^.tok := tok;
    end;

  if rule^.next <> nil then
    begin
      output^.child := SyntaxMatch(a, lexer, rule^.next);
      if output^.child = nil then output := nil;
    end;
  
  SyntaxMatch := output;
end;

function NewParser(a : pArena; lexer : pLexer) : pParser;
var
  output : pParser;
begin
  output := ArenaAllocate(a, sizeof(Parser));
end;
