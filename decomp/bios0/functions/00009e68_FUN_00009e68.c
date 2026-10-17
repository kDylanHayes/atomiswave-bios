/* 00009e68  FUN_00009e68  bytes=314 */
int FUN_00009e68(void)
{
  int iVar1;
  int iVar2;
  short sVar3;
  undefined *puVar4;
  sVar3 = *(short *)(PTR_DAT_00009f00 + 0x90);
  puVar4 = PTR_DAT_00009f00;
  if (sVar3 < 0) {
    FUN_0000a15e();
  }
  if (sVar3 == -8) {
    iVar2 = (*(code *)PTR_FUN_00009fb8)(*(undefined4 *)(puVar4 + 100));
    if (iVar2 != 0) {
      sVar3 = 0x7e;
      goto LAB_00009f82;
    }
LAB_00009f7c:
    sVar3 = 0;
  }
  else {
    if (sVar3 == -7) {
LAB_00009eec:
      iVar2 = FUN_0000a3a0(1);
      if (iVar2 == -2) {
        sVar3 = sVar3 + -2;
      }
      else if (iVar2 == 0) {
        if (*(int *)(puVar4 + 0x4c) == (int)DAT_00009fac) {
          sVar3 = sVar3 + -1;
        }
        else {
          iVar1 = FUN_00009e50();
          if (iVar1 == 0) {
            iVar2 = 1;
          }
          else {
            sVar3 = 0;
          }
        }
      }
      if (iVar2 != 1) goto LAB_00009f82;
      iVar2 = FUN_00009e34();
      if (iVar2 != -1) {
        iVar2 = *(int *)(puVar4 + 0x30);
        if (iVar2 == 2) {
          sVar3 = sVar3 + 2;
          goto LAB_00009f82;
        }
        if (iVar2 == 6) {
LAB_00009f46:
          sVar3 = -2;
          goto LAB_00009f82;
        }
        if (iVar2 != 0x10) {
          sVar3 = -1;
          goto LAB_00009f82;
        }
        iVar2 = FUN_00009e50();
        if (iVar2 == 0) goto LAB_00009f82;
        goto LAB_00009f7c;
      }
    }
    else {
      if (sVar3 != -6) {
        if (sVar3 == -5) {
          (*(code *)PTR_FUN_00009fb4)(PTR_DAT_00009fb0);
          *(undefined4 *)(puVar4 + 0xf8) = *(undefined4 *)(puVar4 + 100);
          FUN_0000a1d4();
          sVar3 = -6;
        }
        else {
          if (sVar3 == -4) goto LAB_00009eec;
          if (sVar3 != -3) {
            if (sVar3 != -2) {
              if (sVar3 == -1) {
                if (*(int *)(puVar4 + 0x30) == 0) {
                  sVar3 = 0x7f;
                }
                else {
                  sVar3 = (short)*(undefined4 *)(puVar4 + 0x30);
                }
                goto LAB_00009f82;
              }
              func_0x00009d52();
              puVar4[0x26] = puVar4[0x26] | 1;
              *(undefined2 *)(puVar4 + 0x46) = 10;
              goto LAB_00009f46;
            }
            *(undefined4 *)(puVar4 + 0xec) = 0x18;
            FUN_0000a1d4();
            sVar3 = -3;
          }
        }
      }
      iVar2 = FUN_0000a3a0(0);
      if (iVar2 != 1) {
        if (iVar2 == 0) {
          sVar3 = sVar3 + -1;
          FUN_0000a1d4();
        }
        goto LAB_00009f82;
      }
    }
    sVar3 = -1;
  }
LAB_00009f82:
  if (sVar3 < *(short *)(puVar4 + 0x92)) {
    sVar3 = 0;
  }
  if (-1 < sVar3) {
    func_0x00009db8();
  }
  *(short *)(puVar4 + 0x90) = sVar3;
  return (int)sVar3;
}
