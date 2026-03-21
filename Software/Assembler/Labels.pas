
type
  TLabel = record
    next : ^TLabel;
    labelName : pString;
    location : cardinal;
  end;
  pLabel = ^TLabel;

var
  labelArena : pArena;
  rootLabel : pLabel;

procedure InstallLabel(labelName : pString);
var
  newLabel : pLabel;
begin
  if labelArena = nil then
    labelArena := NewArena();

  newLabel := ArenaAllocate(labelArena, sizeof(TLabel));
  newLabel^.location := 0;
  newLabel^.labelName := labelName;
  newLabel^.next := rootLabel;

  rootLabel := newLabel;
end;

procedure SetLabelLocation(labelName : pString; location : cardinal);
var
  curLabel : pLabel;
  didSet : boolean;
begin
  curLabel := rootLabel;
  didSet := false;

  while (curLabel <> nil) and (not didSet) do
    begin
      didSet := curLabel^.labelName = labelName;
      if didSet then curLabel^.location := location;
      curLabel := curLabel^.next;
    end;

  if not didSet then
    begin
      writeln('Label does not exist');
      writeln(labelName^.contents);
    end;
end;
