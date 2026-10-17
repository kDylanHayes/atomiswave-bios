/* 0000a370  FUN_0000a370  bytes=48 */
int FUN_0000a370(void)
{
  int iVar1;
  int in_GBR;
  *(undefined2 *)(in_GBR + 0x46) = 10;
  do {
    FUN_0000a1d4();
    iVar1 = FUN_0000a354(0);
    if (iVar1 != 0) {
      return iVar1;
    }
    FUN_0000a1d4();
    while( true ) {
      func_0x00009cdc();
      iVar1 = FUN_0000a3a0(1);
      if (iVar1 == -2) break;
      if (-1 < iVar1) {
        return iVar1;
      }
    }
  } while( true );
}
