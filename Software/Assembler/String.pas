const
  MAX_STR_IDX = 63;
  MAX_STR_LEN = 64;

type
  RawString = array [0..MAX_STR_IDX] of char;

function RawStringLength(str : RawString) : cardinal;
var
  i : cardinal;
begin
  i := 0;

  while (str[i]) <> chr(0) do
    begin
      i := i + 1;
    end;
  
  RawStringLength := i;
end;

function HashRawString(str : RawString) : cardinal;
var
  i, output, length : cardinal;
begin
  output := 5381;
  length := RawStringLength(str);

  for i := 0 to length do
    output := ((output * 32) + output) + ord(str[i]);

  HashRawString := output;
end;

function RawStringCompare(str0, str1 : RawString) : boolean;
var
  output : boolean;
  i, max : cardinal;
begin
  max := RawStringLength(str0);
  output := max = RawStringLength(str1);
  i := 0;

  while (i < max) and (output) do
    begin
      output := output and (str0[i] = str1[i]);
      i := i + 1;
    end;

  RawStringCompare := output;
end;

type
  String = record
    next : ^String;
    hash : cardinal;
    contents : RawString;
  end;
  pString = ^String;

const
  STR_POOL_MAX_IDX = 31;
var
  StringPool : array [0..STR_POOL_MAX_IDX] of pString;
  StringArena : pArena;

function NewString(str : RawString) : pString;
var
  hashIdx, hash : cardinal;
  curStr, output : pString;
begin
  output := nil;
  if StringArena = nil then StringArena := NewArena();

  hash := HashRawString(str);
  hashIdx := hash mod STR_POOL_MAX_IDX;
  curStr := StringPool[hashIdx];

  while (output = nil) and (curStr <> nil) do
    begin
      if (curStr^.hash = hash) and 
        RawStringCompare(curStr^.contents, str)
      then
        output := curStr;
      
      curStr := curStr^.next;
    end;

  if output = nil then
    begin
      output := ArenaAllocate(StringArena, sizeof(String));
      output^.next := StringPool[hashIdx];
      output^.hash := hash;
      output^.contents := str;
      StringPool[hashIdx] := output;
    end;

  NewString := output;
end;
