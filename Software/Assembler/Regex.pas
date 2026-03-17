type 
  RegexKind = (RA_CHAR, RA_BINOP, RA_UNARY);
  Regex = record
    next : ^Regex;
    case kind : RegexKind of
      RA_CHAR : (charContent : char);
      RA_BINOP : (binOp : char; left, right : ^Regex);
      RA_UNARY : (unOp : char; operand : ^Regex);
  end;
  pRegex = ^Regex;

  CharFile = file of char;
  pCharFile = ^CharFile;

  RegexEvalResult = record
    success : boolean;
    length : cardinal;
  end;

function CompileRegex(permArena : pArena; expr : RawString) : pRegex;
type
  RegexTokenKind = (RT_CHAR, RT_DASH, RT_OR, RT_LPAREN, RT_RPAREN, RT_KLEENE, RT_BACKSLASH);
  RegexToken = record
    next : ^RegexToken;
    kind : RegexTokenKind;
    contents : char;
  end;
  pRegexToken = ^RegexToken;
var
  tmpArena : pArena;
  tokenizedRegex : pRegexToken;

  procedure AppendToken(kind : RegexTokenKind; content : char);
  var
    newToken, curToken : pRegexToken;
  begin
    newToken := ArenaAllocate(tmpArena, sizeof(RegexToken));
    newToken^.kind := kind;
    newToken^.contents := content;
    newToken^.next := nil;

    curToken := tokenizedRegex;
    if curToken = nil then
      tokenizedRegex := newToken
    else
      begin
        while curToken^.next <> nil do curToken := curToken^.next;
        curToken^.next := newToken;
      end;
  end;

  function AppendRegex(head, tail : pRegex) : pRegex;
  var
    output : pRegex;
  begin
    if head = nil then
      output := tail
    else
      begin
        output := head;
        while head^.next <> nil do head := head^.next;
        head^.next := tail;
      end;

    AppendRegex := output;
  end;

  procedure TokenizeRegex;
  var
    i, max : cardinal;
    curChar : char;
  begin
    i := 0;
    max := RawStringLength(expr);
    tokenizedRegex := nil;

    while i < max do
      begin
        curChar := expr[i];

        if curChar = '-' then
          AppendToken(RT_DASH, curChar)
        else if curChar = '(' then
          AppendToken(RT_LPAREN, curChar)
        else if curChar = ')' then
          AppendToken(RT_RPAREN, curChar)
        else if curChar = '*' then
          AppendToken(RT_KLEENE, curChar)
        else if curChar = '|' then
          AppendToken(RT_OR, curChar)
        else if curChar = '\' then
          begin
            i := i + 1;
            AppendToken(RT_CHAR, expr[i]);
          end
        else
          AppendToken(RT_CHAR, curChar);

        i := i + 1;
      end;
  end;

  function ParseRegex() : pRegex;    
    function ParsePrefix() : pRegex;
    var
      output : pRegex;
    begin
      output := nil;

      if tokenizedRegex = nil then
        output := nil
      else if (tokenizedRegex^.kind) = RT_CHAR then
        begin
          output := ArenaAllocate(permArena, sizeof(Regex));
          output^.kind := RA_CHAR;
          output^.charContent := tokenizedRegex^.contents;
          output^.next := nil;
          tokenizedRegex := tokenizedRegex^.next;
        end
      else if (tokenizedRegex^.kind) = RT_LPAREN then
        begin
          tokenizedRegex := tokenizedRegex^.next;
          output := ParseRegex();
          output^.next := nil;
          if (tokenizedRegex^.kind) <> RT_RPAREN then 
            begin
              writeln(tokenizedRegex^.contents);
              writeln('unmatched paren');
              output := nil;
            end;
          tokenizedRegex := tokenizedRegex^.next;
        end;

      ParsePrefix := output; { TODO }
    end;

    function ParseInfix(lhs : pRegex) : pRegex;
    var
      output : pRegex;
    begin
      output := nil;


      if (lhs = nil) or 
        (tokenizedRegex = nil)
      then
        output := nil { Do nothing }
      else if 
        (tokenizedRegex^.kind = RT_DASH) or
        (tokenizedRegex^.kind = RT_OR)
      then
        begin
          output := ArenaAllocate(permArena, sizeof(Regex));
          output^.kind := RA_BINOP;
          output^.next := nil;
          output^.binOp := tokenizedRegex^.contents;
          output^.left := lhs;
          tokenizedRegex := tokenizedRegex^.next;
          output^.right := ParseRegex();

          if 
            (output^.right = nil) or
            ((output^.binOp = '-') and
            ((output^.right^.kind <> RA_CHAR) or 
            (output^.left^.kind <> RA_CHAR)))
          then
            output := nil;
        end;


      ParseInfix := output;
    end;

    function ParsePostfix(prefix : pRegex) : pRegex;
    var
      output : pRegex;
    begin
      output := nil;

      if (prefix <> nil) and
        (tokenizedRegex <> nil) and
        (tokenizedRegex^.kind = RT_KLEENE)
      then
        begin
          output := ArenaAllocate(permArena, sizeof(Regex));
          output^.kind := RA_UNARY;
          output^.next := nil;
          output^.unOp := tokenizedRegex^.contents;
          output^.operand := prefix;
          tokenizedRegex := tokenizedRegex^.next;
        end;

      ParsePostfix := output;
    end;

  var
    output, tmp, current : pRegex;
  begin
    output := nil;

    repeat
      current := ParsePrefix();

      tmp := ParseInfix(current);
      if tmp <> nil then current := tmp;

      tmp := ParsePostfix(current);
      if tmp <> nil then current := tmp;

      if current <> nil then
        output := AppendRegex(output, current);
    until (current = nil);

    ParseRegex := output;
  end;
  
var
  output : pRegex;
begin
  tmpArena := NewArena();
  TokenizeRegex;

  output := ParseRegex();

  DestroyArena(tmpArena);
  CompileRegex := output;
end;

function EvaluateRegex(reg : pRegex; inputFile : pCharFile) : RegexEvalResult;
var
  output, next : RegexEvalResult;
  curChar : char;
  startPos : cardinal;

  procedure FailState();
  begin
    output.success := false;
    output.length := 0;
    seek(inputFile^, startPos);
  end;

begin
  startPos := filepos(inputFile^);

  if (reg = nil) then
    begin
      output.success := true;
      output.length := 0;
    end
  else if (eof(inputFile^)) then
    FailState()
  else if (reg^.kind = RA_CHAR) then
    begin
      read(inputFile^, curChar);
      if (curChar = reg^.charContent) then
        begin 
          output := EvaluateRegex(reg^.next, inputFile);
          output.length := output.length + 1; 
        end
      else FailState;
    end
  else if (reg^.kind = RA_BINOP) and (reg^.binOp = '-') then
    begin
      read(inputFile^, curChar);
      if 
        (ord(curChar) >= ord(reg^.left^.charContent)) and 
        (ord(curChar) <= ord(reg^.right^.charContent))
      then
        begin
          output := EvaluateRegex(reg^.next, inputFile);
          output.length := output.length + 1;
        end
      else FailState();
    end
  else if (reg^.kind = RA_BINOP) and (reg^.binOp = '|') then
    begin
      next := EvaluateRegex(reg^.left, inputFile);
      if (not next.success) then next := EvaluateRegex(reg^.right, inputFile);

      if next.success then
        begin
          output := EvaluateRegex(reg^.next, inputFile);
          output.length := next.length + output.length;
        end
      else FailState();
    end
  else if (reg^.kind = RA_UNARY) and (reg^.unOp = '*') then
    begin
      output.length := 0;
      output.success := true;
      repeat
        next := EvaluateRegex(reg^.operand, inputFile);
        if (next.success) then
          begin
            output.length := output.length + next.length;
          end
      until (not next.success);

      next := EvaluateRegex(reg^.next, inputFile);
      output.success := next.success;
      output.length := output.length + next.length;
    end
  else FailState();
  

  EvaluateRegex := output;
end;

function EvaluateRegexString(reg : pRegex; inputFile : pCharFile) : pString;
var
  raw : RawString;
  output : pString;
  match : RegexEvalResult;
  pos, i : cardinal;
begin
  pos := filepos(inputFile^);
  output := nil;
  match := EvaluateRegex(reg, inputFile);
  seek(inputFile^, pos);

  if match.success and (match.length < MAX_STR_IDX) then
    begin
      for i := 0 to match.length-1 do
        begin
          read(inputFile^, raw[i]);
        end;
        raw[match.length] := chr(0);
        output := NewString(raw);
    end;

  EvaluateRegexString := output;
end;
