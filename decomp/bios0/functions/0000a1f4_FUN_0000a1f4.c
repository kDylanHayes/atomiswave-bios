/* 0000a1f4  FUN_0000a1f4  bytes=322 */
int FUN_0000a1f4(byte *param_1,undefined4 param_2)
{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  byte *pbVar7;
  byte *pbVar8;
  int in_GBR;
  (*(code *)PTR_FUN_0000a2f0)(param_1);
  *(undefined4 *)(in_GBR + 0xec) = 0x11;
  *(undefined4 *)(in_GBR + 0xf0) = param_2;
  *(undefined4 *)(in_GBR + 0xf4) = 1;
  *(byte **)(in_GBR + 0xf8) = param_1;
  *(undefined4 *)(in_GBR + 0xfc) = 0;
  iVar3 = FUN_0000a370();
  if ((iVar3 == 0) && (iVar3 = (*(code *)PTR_FUN_0000a2f4)(param_1), iVar3 == 0)) {
    iVar3 = func_0x00009ce2(param_1 + DAT_0000a2e8);
    *(int *)(in_GBR + 0xf0) = iVar3 + DAT_0000a2ea;
    *(undefined4 *)(in_GBR + 0xf4) = 1;
    *(byte **)(in_GBR + 0xf8) = param_1;
    *(undefined4 *)(in_GBR + 0xfc) = 0;
    *(undefined4 *)(in_GBR + 0xec) = 0x11;
    FUN_0000a370();
    uVar2 = DAT_0000a2f8;
    iVar6 = (int)DAT_0000a2ea;
    iVar3 = (int)DAT_0000a2ec;
    for (pbVar8 = param_1; (*pbVar8 != 0 && (pbVar8 < param_1 + iVar3)); pbVar8 = pbVar8 + *pbVar8)
    {
      if ((pbVar8[0x19] & 2) == 0) {
        pbVar7 = pbVar8 + pbVar8[0x20] + 0x21;
        bVar1 = *pbVar7;
        *pbVar7 = 0x3b;
        iVar4 = (*(code *)PTR_FUN_0000a2fc)(*(undefined4 *)(in_GBR + 0x9c));
        if (iVar4 == 0) {
          iVar3 = func_0x00009ce2(pbVar8 + 0xe);
          iVar4 = func_0x00009ce2(pbVar8 + 6);
          if (((uint)(iVar4 + iVar6) < uVar2) && (*(char *)(in_GBR + 0x24) != '\x02')) {
            (*(code *)PTR_FUN_0000a300)(1);
          }
          *(int *)(in_GBR + 0xf0) = iVar4 + iVar6;
          *(uint *)(in_GBR + 0xf4) = (uint)(DAT_0000a2ee + iVar3) >> 0xb;
          if (*(char *)(in_GBR + 0x24) != '\0') {
            param_1 = (byte *)0x0;
          }
          *(byte **)(in_GBR + 0xf8) = param_1;
          iVar6 = iVar3;
          if (*(char *)(in_GBR + 0x24) == '\0') {
            iVar6 = 0;
          }
          *(int *)(in_GBR + 0xfc) = iVar6;
          *(undefined2 *)(in_GBR + 0x46) = 10;
          FUN_0000a1d4();
          if (*(char *)(in_GBR + 0x24) == '\0') {
            uVar5 = 0x11;
          }
          else {
            uVar5 = 0x1c;
          }
          *(undefined4 *)(in_GBR + 0xec) = uVar5;
          FUN_0000a354(0);
          func_0x00009cdc();
          return iVar3;
        }
        *pbVar7 = bVar1;
      }
    }
  }
  return 0;
}
