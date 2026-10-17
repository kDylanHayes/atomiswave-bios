/* 000007a4  program_bootrom  bytes=284 */
void program_bootrom(void)
{
  undefined *puVar1;
  int iVar2;
  undefined4 *puVar3;
  int *piVar4;
  char *pcVar5;
  undefined *puVar6;
  int *piVar7;
  undefined *puVar8;
  undefined1 *puVar9;
  uint *puVar10;
  uint uVar11;
  int iVar12;
  undefined1 *puVar13;
  undefined *puVar14;
  undefined4 uVar15;
  int iVar16;
  undefined4 uVar17;
  uint uVar18;
  iVar12 = 0x10;
  piVar4 = (int *)PTR_DAT_000007bc;
  piVar7 = DAT_000007c0;
  while( true ) {
    iVar2 = *piVar4;
    piVar4 = piVar4 + 1;
    iVar16 = *piVar7;
    piVar7 = piVar7 + 1;
    if (iVar16 != iVar2) break;
    iVar12 = iVar12 + -1;
    if (iVar12 == 0) goto LAB_000008c0;
  }
  blit_glyphs();
  blit_glyphs();
  uVar15 = DAT_00000808;
  puVar3 = DAT_0000080c;
  puVar8 = PTR_DAT_00000810;
  do {
    *puVar3 = uVar15;
    puVar3 = puVar3 + 1;
    puVar8 = puVar8 + -1;
  } while (puVar8 != (undefined *)0x0);
  puVar9 = (undefined1 *)*DAT_00000840;
  puVar13 = (undefined1 *)DAT_00000840[1];
  uVar15 = DAT_00000840[2];
  iVar12 = DAT_00000840[3];
  uVar17 = DAT_00000840[4];
  iVar2 = DAT_00000840[5];
  puVar3 = DAT_00000840 + 6;
  do {
    pcVar5 = (char *)*puVar3;
    puVar3 = puVar3 + 1;
    *puVar9 = (char)puVar13;
    *puVar13 = (char)puVar9;
    *puVar9 = (char)uVar15;
    *puVar9 = (char)puVar13;
    *puVar13 = (char)puVar9;
    *pcVar5 = (char)uVar17;
    puVar1 = PTR_DAT_000008b0;
    puVar8 = PTR_DAT_000008ac;
    do {
    } while (iVar12 != *pcVar5);
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  iVar12 = 0x10;
  puVar10 = DAT_000008a4;
  puVar14 = PTR_DAT_000008a8;
  do {
    uVar11 = *puVar10;
    puVar10 = puVar10 + 1;
    iVar2 = 4;
    do {
      *puVar8 = 0xaa;
      *puVar1 = 0x55;
      *puVar8 = 0xa0;
      *puVar14 = (char)uVar11;
      puVar6 = PTR_DAT_000008b4;
      do {
        puVar6 = puVar6 + -1;
      } while (puVar6 != (undefined *)0x0);
      puVar14 = puVar14 + 1;
      uVar11 = uVar11 >> 8;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    iVar12 = iVar12 + -1;
  } while (iVar12 != 0);
  poll_bit();
LAB_000008c0:
  puVar8 = PTR_DAT_0000092c;
  uVar11 = *(uint *)(DAT_00000918 + DAT_0000091c);
  uVar15 = *(undefined4 *)(DAT_00000918 + DAT_00000920);
  uVar17 = *(undefined4 *)(DAT_00000918 + DAT_00000924);
  uVar18 = *(uint *)(DAT_00000918 + DAT_00000928);
  *(uint *)PTR_DAT_0000092c = uVar11 >> 1;
  *(uint *)(puVar8 + 4) = uVar11 >> 0x11;
  puVar8 = PTR_DAT_00000930;
  *(undefined4 *)PTR_DAT_00000930 = uVar15;
  *(undefined4 *)(puVar8 + 4) = uVar17;
  *(undefined4 *)(puVar8 + 8) = 1;
  *(undefined4 *)(puVar8 + 0x10) = 1;
  *(uint *)(puVar8 + 0x14) = 1;
  do {
  } while ((*(uint *)(puVar8 + 0x14) & 1) != 0);
  *(undefined4 *)(puVar8 + 0x10) = 0;
  *(undefined4 *)PTR_CCR_0000096c = DAT_00000970;
                    /* runtime handoff: jmp 0xA0000000 | *(uint32 *)0x01AC006C */
  (*(code *)((uint)PTR_reset_00000978 | uVar18))();
  return;
}
