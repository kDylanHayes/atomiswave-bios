/* 00000600  exc_interrupt  bytes=116 */
void exc_interrupt(void)
{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined *puVar3;
  uint uVar4;
  undefined4 *in_r1;
  undefined4 *puVar5;
  short *psVar6;
  int in_r2;
  int iVar8;
  uint *puVar9;
  int iVar10;
  int iVar11;
  undefined4 *puVar12;
  int iVar13;
  uint *puVar14;
  uint *puVar15;
  uint *puVar16;
  short *psVar7;
  while( true ) {
    uVar2 = DAT_000006ec;
    uVar1 = DAT_000006a0;
    in_r1 = (undefined4 *)((int)in_r1 + DAT_000006a4);
    in_r2 = in_r2 + -1;
    puVar5 = DAT_000006f4;
    iVar8 = DAT_0000069c;
    iVar11 = DAT_000006f0;
    puVar12 = in_r1;
    if (in_r2 == 0) break;
    do {
      *puVar12 = uVar2;
      iVar11 = iVar11 + -1;
      puVar12 = puVar12 + 1;
    } while (iVar11 != 0);
  }
  do {
    *puVar5 = uVar1;
    iVar8 = iVar8 + -1;
    psVar6 = DAT_000006f8;
    puVar5 = puVar5 + 1;
    iVar11 = DAT_000006c8;
    puVar14 = DAT_000006fc;
    iVar10 = DAT_000006c4;
    puVar9 = DAT_000006fc;
  } while (iVar8 != 0);
  do {
    do {
      psVar7 = psVar6 + 1;
      uVar4 = (int)*psVar6 & (uint)PTR_DAT_000006b0;
      iVar8 = DAT_000006c8;
      puVar16 = puVar14;
      puVar15 = puVar14;
      iVar13 = DAT_000006bc;
      do {
        do {
          *puVar16 = uVar4 << 0x10 | uVar4;
          iVar8 = iVar8 + -1;
          puVar16 = puVar16 + 1;
        } while (iVar8 != 0);
        puVar16 = (uint *)((int)puVar15 + DAT_000006a4);
        iVar13 = iVar13 + -1;
        iVar8 = DAT_000006c8;
        puVar15 = puVar16;
      } while (iVar13 != 0);
      iVar11 = iVar11 + -1;
      psVar6 = psVar7;
      puVar14 = (uint *)((int)puVar14 + DAT_000006bc);
    } while (iVar11 != 0);
    iVar10 = iVar10 + -1;
    puVar5 = DAT_00000704;
    iVar11 = DAT_000006c8;
    iVar8 = DAT_000006c0;
    puVar14 = (uint *)((int)puVar9 + (int)PTR_DAT_00000700);
    puVar9 = (uint *)((int)puVar9 + (int)PTR_DAT_00000700);
  } while (iVar10 != 0);
  do {
    do {
      puVar3 = PTR_DAT_00000708;
      *(undefined4 *)PTR_DAT_00000708 = *puVar5;
      puVar12 = puVar5 + 2;
      *(undefined4 *)(puVar3 + 4) = puVar5[1];
      poll_bit();
      iVar8 = iVar8 + -1;
      puVar5 = puVar12;
    } while (iVar8 != 0);
    puVar5 = DAT_00000704;
    iVar8 = DAT_000006c0;
  } while( true );
}
