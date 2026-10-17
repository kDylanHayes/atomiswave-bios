/* 00000100  exc_general  bytes=214 */
void exc_general(void)
{
  undefined2 uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined2 in_r0;
  undefined4 uVar4;
  int in_r1;
  int *piVar5;
  undefined2 *puVar6;
  undefined2 *in_r2;
  undefined4 *puVar7;
  undefined4 *puVar8;
  undefined2 *puVar9;
  int extraout_r2;
  int extraout_r2_00;
  int iVar10;
  undefined8 uVar11;
  *in_r2 = in_r0;
  *(short *)PTR_RFCR_00000144 = (short)*(undefined4 *)(in_r1 + 0x20);
  *(undefined4 *)PTR_MCR_0000014c = *(undefined4 *)(in_r1 + 0x24);
  do {
  } while (*(ushort *)PTR_RFCR_00000144 < 9);
  iVar10 = *DAT_00000238;
  puVar7 = DAT_0000023c;
  piVar5 = DAT_00000238;
  do {
    piVar5 = piVar5 + 1;
    uVar4 = *puVar7;
    puVar7 = puVar7 + 1;
    *(undefined4 *)*piVar5 = uVar4;
    puVar8 = DAT_000002a4;
    puVar3 = DAT_0000025c;
    puVar2 = DAT_00000248;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  if (((uint)(int)*(short *)PTR_DAT_00000240 >> 8 & 3) == 0) {
    *DAT_00000244 = 1;
  }
  else if (((uint)(int)*(short *)PTR_DAT_00000240 >> 8 & 1) == 0) {
    *DAT_00000244 = DAT_00000260;
    puVar8 = puVar3;
  }
  else {
    *DAT_00000244 = DAT_0000024c;
    puVar8 = puVar2;
  }
  iVar10 = *DAT_000002a8;
  piVar5 = DAT_000002a8;
  do {
    piVar5 = piVar5 + 1;
    uVar4 = *puVar8;
    puVar8 = puVar8 + 1;
    *(undefined4 *)*piVar5 = uVar4;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  iVar10 = 0xc;
  puVar6 = DAT_000002ac;
  puVar9 = DAT_000002b0;
  do {
    uVar1 = *puVar6;
    puVar6 = puVar6 + 1;
    *puVar9 = uVar1;
    puVar9 = puVar9 + 1;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  *(undefined4 *)PTR_DAT_000002b4 = DAT_000002b8;
  if ((*DAT_000002bc & 3) != 0) {
    do {
      uVar11 = mix_shifts();
      *(undefined4 *)((ulonglong)uVar11 >> 0x20) = (int)uVar11;
    } while (extraout_r2 != 1);
    do {
      uVar11 = mix_shifts();
      if ((int)uVar11 != *(int *)((ulonglong)uVar11 >> 0x20)) {
        *(undefined4 *)PTR_DAT_00000314 = DAT_00000310;
        init_memory();
        return;
      }
    } while (extraout_r2_00 != 1);
    init_memory();
    return;
  }
  init_memory();
  return;
}
