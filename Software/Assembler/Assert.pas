procedure Assert(expr : boolean);
begin
  if not expr then 
    begin
      writeln('assertion failed');
      exit;
    end;
end;
