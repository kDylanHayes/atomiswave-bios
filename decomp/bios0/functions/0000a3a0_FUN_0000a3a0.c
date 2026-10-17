/* 0000a3a0  FUN_0000a3a0  bytes=236 */
int FUN_0000a3a0(int param_1)
{
  int iVar1;
  int iVar2;
  int in_GBR;
  iVar2 = 1;
  if (param_1 == 0) {
    iVar1 = (*(code *)PTR_FUN_0000a3cc)(*(undefined4 *)(in_GBR + 0xec),in_GBR + DAT_0000a3c8,0);
    *(int *)(in_GBR + 0x40) = iVar1;
    if (iVar1 != 0) {
      iVar2 = 0;
    }
    goto LAB_0000a458;
  }
  iVar1 = (*(code *)PTR_FUN_0000a494)(*(undefined4 *)(in_GBR + 0x40),in_GBR + 0x30,0,1);
  *(int *)(in_GBR + 0xe8) = iVar1;
  if (iVar1 == 2) {
LAB_0000a41e:
    iVar2 = 0;
  }
  else if (iVar1 == -1) {
    *(undefined2 *)(in_GBR + 0x44) = 0;
    iVar1 = *(int *)(in_GBR + 0x30);
    if (((((iVar1 == 0) || (iVar1 == 1)) || (iVar1 == 2)) || ((iVar1 == 5 || (iVar1 == 6)))) ||
       ((iVar1 == 0xb || (iVar1 == 0x10)))) {
      *(undefined2 *)(in_GBR + 0x46) = 0;
    }
  }
  else {
    if (iVar1 == 0) goto LAB_0000a41e;
    if ((iVar1 == 1) || (iVar1 == 3)) {
      iVar2 = -1;
    }
  }
  if (((iVar2 != -1) && (iVar1 = (*(code *)PTR_FUN_0000a494)(in_GBR + 0x48,0,4), iVar1 == 0)) &&
     (iVar1 = FUN_00009e34(), iVar1 == -1)) {
    *(undefined2 *)(in_GBR + 0x44) = 0;
    *(undefined2 *)(in_GBR + 0x46) = 0;
  }
LAB_0000a458:
  if ((iVar2 == 1) || (iVar2 == -1)) {
    if (*(short *)(in_GBR + 0x44) == 0) {
      if (*(short *)(in_GBR + 0x46) != 0) {
        *(short *)(in_GBR + 0x46) = *(short *)(in_GBR + 0x46) + (short)PTR_DAT_0000a498;
        FUN_0000a1d4();
        iVar2 = -2;
      }
    }
    else {
      *(short *)(in_GBR + 0x44) = *(short *)(in_GBR + 0x44) + (short)PTR_DAT_0000a498;
      iVar2 = -1;
    }
  }
  return iVar2;
}
