
type
  AstKind = (ORG, DEF);
  Ast = record


    case kind : AstKind of
      ORG : (location : cardinal);
      DEF : (labelName : pString);
  end;
  pAst = ^Ast;

  ParseFn = function (arena : pArena; lex : pLexer) : pAst;
  Parser = record
    fn : ParseFn;
    next : ^Parser;
    alternate : ^Parser;
  end;
  pParser = ^Parser;
