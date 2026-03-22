
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

function GetLabel(labelName : pString) : pLabel;
var
  curLabel : pLabel;
begin
  curLabel := rootLabel;
  
  while (curLabel <> nil) and (curLabel^.labelName <> labelName) do
    curLabel := curLabel^.next;

  GetLabel := curLabel;
end;
