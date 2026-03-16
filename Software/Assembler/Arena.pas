type
  Allocation = record
    next : ^Allocation;
    size : cardinal;
    value : pointer;
  end;
  pAllocation = ^Allocation;

  Arena = record
    allocations : ^Allocation;
  end;
  pArena = ^Arena;

function NewArena() : pArena;
var
  output : pArena;
begin
  getmem(output, sizeof(Arena));
  output^.allocations := nil;
  NewArena := output;
end;

function ArenaAllocate(a : pArena; size : cardinal) : pointer;
var
  allocation : pAllocation;
begin
  getmem(allocation, sizeof(Allocation));
  allocation^.next := a^.allocations;
  a^.allocations := allocation;

  getmem(allocation^.value, size);
  allocation^.size := size;

  ArenaAllocate := allocation^.value;
end;

procedure DestroyArena(a : pArena);
var
  curAlloc, freeMe : ^Allocation;
begin
  curAlloc := a^.allocations;

  while curAlloc <> nil do
    begin
      FreeMem(curAlloc^.value, curAlloc^.size);
      freeMe := curAlloc;
      curAlloc := curAlloc^.next;
      freemem(freeMe, sizeof(Allocation));
    end;

  freemem(a, sizeof(Arena));
end;
