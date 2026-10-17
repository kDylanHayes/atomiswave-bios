/* 00009e34  FUN_00009e34  bytes=28 */
undefined4 FUN_00009e34(void)
{
  int iVar1;
  undefined4 uVar2;
  int in_GBR;
  iVar1 = *(int *)(in_GBR + 0x48);
  if (((iVar1 == 6) || (iVar1 == 7)) || (iVar1 == 9)) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}
