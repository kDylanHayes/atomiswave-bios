/* 0000005c  boot  bytes=146 */
void boot(void)
{
  undefined2 uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  int *piVar6;
  undefined2 *puVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  undefined2 *puVar10;
  int extraout_r2;
  int extraout_r2_00;
  int iVar11;
  undefined8 uVar12;
  puVar8 = DAT_00000120;
  uVar5 = DAT_00000074 | (uint)PTR_reset_00000078;
  do {
    uVar5 = uVar5 + 4;
  } while (uVar5 < ((uint)PTR_DAT_0000007c | (uint)PTR_reset_00000078));
  *(undefined4 *)PTR_BCR1_00000124 = *DAT_00000120;
  *(short *)PTR_BCR2_00000128 = (short)puVar8[1];
  *(undefined4 *)PTR_WCR1_0000012c = puVar8[2];
  *(undefined4 *)PTR_WCR2_00000130 = puVar8[3];
  *(undefined4 *)PTR_WCR3_00000134 = puVar8[4];
  *(short *)PTR_RTCSR_00000138 = (short)puVar8[5];
  *(short *)PTR_RTCOR_0000013c = (short)puVar8[6];
  *(short *)PTR_RTCNT_00000140 = (short)puVar8[7];
  *(short *)PTR_RFCR_00000144 = (short)puVar8[8];
  *(uint *)PTR_MCR_0000014c = puVar8[9] & DAT_00000148;
  *(undefined1 *)puVar8[10] = 0xff;
  *(undefined4 *)PTR_MCR_0000014c = puVar8[9];
  do {
  } while (*(ushort *)PTR_RFCR_00000144 < 9);
  *(uint *)PTR_MCR_0000014c = puVar8[9] & DAT_00000148;
  *(undefined1 *)puVar8[10] = 0xff;
  *(short *)PTR_RTCSR_00000138 = (short)puVar8[5];
  *(short *)PTR_RTCOR_0000013c = (short)puVar8[6];
  *(short *)PTR_RTCNT_00000140 = (short)puVar8[7];
  *(short *)PTR_RFCR_00000144 = (short)puVar8[8];
  *(undefined4 *)PTR_MCR_0000014c = puVar8[9];
  do {
  } while (*(ushort *)PTR_RFCR_00000144 < 9);
  iVar11 = *DAT_00000238;
  puVar8 = DAT_0000023c;
  piVar6 = DAT_00000238;
  do {
    piVar6 = piVar6 + 1;
    uVar4 = *puVar8;
    puVar8 = puVar8 + 1;
    *(undefined4 *)*piVar6 = uVar4;
    puVar9 = DAT_000002a4;
    puVar3 = DAT_0000025c;
    puVar2 = DAT_00000248;
    iVar11 = iVar11 + -1;
  } while (iVar11 != 0);
  if (((uint)(int)*(short *)PTR_DAT_00000240 >> 8 & 3) == 0) {
    *DAT_00000244 = 1;
  }
  else if (((uint)(int)*(short *)PTR_DAT_00000240 >> 8 & 1) == 0) {
    *DAT_00000244 = DAT_00000260;
    puVar9 = puVar3;
  }
  else {
    *DAT_00000244 = DAT_0000024c;
    puVar9 = puVar2;
  }
  iVar11 = *DAT_000002a8;
  piVar6 = DAT_000002a8;
  do {
    piVar6 = piVar6 + 1;
    uVar4 = *puVar9;
    puVar9 = puVar9 + 1;
    *(undefined4 *)*piVar6 = uVar4;
    iVar11 = iVar11 + -1;
  } while (iVar11 != 0);
  iVar11 = 0xc;
  puVar7 = DAT_000002ac;
  puVar10 = DAT_000002b0;
  do {
    uVar1 = *puVar7;
    puVar7 = puVar7 + 1;
    *puVar10 = uVar1;
    puVar10 = puVar10 + 1;
    iVar11 = iVar11 + -1;
  } while (iVar11 != 0);
  *(undefined4 *)PTR_DAT_000002b4 = DAT_000002b8;
  if ((*DAT_000002bc & 3) != 0) {
    do {
      uVar12 = mix_shifts();
      *(undefined4 *)((ulonglong)uVar12 >> 0x20) = (int)uVar12;
    } while (extraout_r2 != 1);
    do {
      uVar12 = mix_shifts();
      if ((int)uVar12 != *(int *)((ulonglong)uVar12 >> 0x20)) {
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
