/* 0000099c  blit_glyphs  bytes=70 */
void blit_glyphs(void)
{
  char cVar1;
  short sVar2;
  undefined2 uVar3;
  char *in_r1;
  undefined2 *in_r2;
  int in_r3;
  int iVar4;
  int iVar5;
  undefined2 *puVar6;
  undefined2 *puVar7;
  short *psVar8;
  undefined *puVar9;
  do {
    cVar1 = *in_r1;
    in_r1 = in_r1 + 1;
    psVar8 = (short *)((((int)cVar1 & DAT_000009e4) - 0x20) * 0x20 + DAT_000009e8);
    iVar4 = 0x10;
    puVar6 = in_r2;
    do {
      sVar2 = *psVar8;
      psVar8 = psVar8 + 1;
      iVar5 = 0x10;
      puVar7 = puVar6;
      puVar9 = PTR_DAT_000009ec;
      do {
        uVar3 = SUB42(PTR_DAT_000009f0,0);
        if (((int)sVar2 & (uint)puVar9) != 0) {
          uVar3 = SUB42(PTR_DAT_000009f4,0);
        }
        *puVar7 = uVar3;
        puVar7 = puVar7 + 1;
        puVar9 = (undefined *)((uint)puVar9 >> 1);
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
      puVar6 = (undefined2 *)((int)puVar6 + DAT_000009f8);
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
    in_r2 = (undefined2 *)((int)in_r2 + DAT_000009fc);
    in_r3 = in_r3 + -1;
  } while (in_r3 != 0);
  return;
}
