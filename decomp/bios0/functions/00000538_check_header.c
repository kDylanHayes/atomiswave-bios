/* 00000538  check_header  bytes=190 */
void check_header(void)
{
  undefined4 uVar1;
  int iVar2;
  undefined *puVar3;
  undefined4 uVar4;
  uint uVar5;
  int *piVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  short *psVar10;
  int iVar12;
  int iVar13;
  uint *puVar14;
  int iVar15;
  int *piVar16;
  undefined4 *puVar17;
  uint *puVar18;
  uint *puVar19;
  uint *puVar20;
  short *psVar11;
  iVar15 = 4;
  piVar6 = DAT_00000550;
  piVar16 = DAT_0000054c;
  do {
    iVar2 = *piVar6;
    piVar6 = piVar6 + 1;
    iVar12 = *piVar16;
    piVar16 = piVar16 + 1;
    if (iVar12 != iVar2) {
      blit_glyphs();
      blit_glyphs();
      poll_bit();
      uVar4 = DAT_000006a0;
      puVar17 = DAT_00000698;
      iVar15 = DAT_0000069c;
      do {
        *puVar17 = uVar4;
        iVar2 = DAT_000006a4;
        puVar17 = puVar17 + 1;
        iVar15 = iVar15 + -1;
        puVar7 = DAT_00000698;
        iVar12 = DAT_000006a8;
      } while (iVar15 != 0);
      do {
        puVar3 = PTR_DAT_000006b0;
        puVar17 = puVar7;
        iVar15 = DAT_000006ac;
        if (iVar12 == DAT_000006b4) {
          puVar3 = DAT_000006b8;
        }
        do {
          *puVar17 = puVar3;
          puVar17 = (undefined4 *)((int)puVar17 + iVar2);
          iVar15 = iVar15 + -1;
        } while (iVar15 != 0);
        puVar7 = (undefined4 *)((int)puVar7 + DAT_000006bc);
        if (iVar12 == DAT_000006c0) {
          puVar7 = (undefined4 *)((int)puVar7 - DAT_000006c4);
        }
        iVar12 = iVar12 + -1;
        iVar15 = DAT_000006cc;
        puVar17 = DAT_00000698;
        iVar13 = DAT_000006c8;
        puVar8 = DAT_00000698;
      } while (iVar12 != 0);
      do {
        do {
          iVar2 = DAT_000006d8;
          puVar7 = puVar17;
          uVar4 = DAT_000006d0;
          if (DAT_000006c0 == iVar15) {
            uVar4 = DAT_000006d4;
          }
          do {
            *puVar7 = uVar4;
            iVar2 = iVar2 + -1;
            puVar7 = puVar7 + 1;
          } while (iVar2 != 0);
          iVar15 = iVar15 + -1;
          puVar17 = (undefined4 *)((int)puVar17 + DAT_000006a4);
        } while (iVar15 != 0);
        puVar17 = (undefined4 *)((int)puVar8 + (int)PTR_LAB_000006dc);
        if (iVar13 == DAT_000006c0) {
          puVar17 = (undefined4 *)((int)puVar17 - DAT_000006e0);
        }
        iVar13 = iVar13 + -1;
        iVar2 = DAT_000006f0;
        puVar7 = DAT_000006e4;
        iVar15 = DAT_000006cc;
        puVar8 = puVar17;
        uVar4 = DAT_000006ec;
        iVar12 = DAT_000006e8;
        puVar9 = DAT_000006e4;
      } while (iVar13 != 0);
      do {
        do {
          *puVar7 = uVar4;
          uVar1 = DAT_000006a0;
          iVar2 = iVar2 + -1;
          puVar7 = puVar7 + 1;
        } while (iVar2 != 0);
        iVar12 = iVar12 + -1;
        puVar17 = DAT_000006f4;
        iVar15 = DAT_0000069c;
        iVar2 = DAT_000006f0;
        puVar7 = (undefined4 *)((int)puVar9 + DAT_000006a4);
        uVar4 = DAT_000006ec;
        puVar9 = (undefined4 *)((int)puVar9 + DAT_000006a4);
      } while (iVar12 != 0);
      do {
        *puVar17 = uVar1;
        iVar15 = iVar15 + -1;
        psVar10 = DAT_000006f8;
        puVar17 = puVar17 + 1;
        iVar2 = DAT_000006c8;
        puVar18 = DAT_000006fc;
        iVar12 = DAT_000006c4;
        puVar14 = DAT_000006fc;
      } while (iVar15 != 0);
      do {
        do {
          psVar11 = psVar10 + 1;
          uVar5 = (int)*psVar10 & (uint)PTR_DAT_000006b0;
          iVar15 = DAT_000006c8;
          puVar20 = puVar18;
          puVar19 = puVar18;
          iVar13 = DAT_000006bc;
          do {
            do {
              *puVar20 = uVar5 << 0x10 | uVar5;
              iVar15 = iVar15 + -1;
              puVar20 = puVar20 + 1;
            } while (iVar15 != 0);
            puVar20 = (uint *)((int)puVar19 + DAT_000006a4);
            iVar13 = iVar13 + -1;
            iVar15 = DAT_000006c8;
            puVar19 = puVar20;
          } while (iVar13 != 0);
          iVar2 = iVar2 + -1;
          psVar10 = psVar11;
          puVar18 = (uint *)((int)puVar18 + DAT_000006bc);
        } while (iVar2 != 0);
        iVar12 = iVar12 + -1;
        puVar17 = DAT_00000704;
        iVar2 = DAT_000006c8;
        iVar15 = DAT_000006c0;
        puVar18 = (uint *)((int)puVar14 + (int)PTR_DAT_00000700);
        puVar14 = (uint *)((int)puVar14 + (int)PTR_DAT_00000700);
      } while (iVar12 != 0);
      do {
        do {
          puVar3 = PTR_DAT_00000708;
          *(undefined4 *)PTR_DAT_00000708 = *puVar17;
          puVar7 = puVar17 + 2;
          *(undefined4 *)(puVar3 + 4) = puVar17[1];
          poll_bit();
          iVar15 = iVar15 + -1;
          puVar17 = puVar7;
        } while (iVar15 != 0);
        puVar17 = DAT_00000704;
        iVar15 = DAT_000006c0;
      } while( true );
    }
    iVar15 = iVar15 + -1;
  } while (iVar15 != 0);
  program_bootrom();
  return;
}
