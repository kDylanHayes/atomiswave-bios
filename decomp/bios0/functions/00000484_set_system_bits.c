/* 00000484  set_system_bits  bytes=106 */
void set_system_bits(void)
{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  *(uint *)PTR_DAT_000004f0 = *(uint *)PTR_DAT_000004f0 | 5;
  do {
  } while ((*(uint *)PTR_DAT_000004f4 & (uint)PTR_DAT_000004f8) != 0);
  *(uint *)PTR_DAT_000004fc = *(uint *)PTR_DAT_000004fc & 0xfffffff7;
  poll_bit();
  *(uint *)PTR_DAT_000004fc = *(uint *)PTR_DAT_000004fc | 8;
  uVar1 = DAT_00000510;
  puVar2 = DAT_00000508;
  iVar3 = DAT_0000050c;
  do {
    *puVar2 = uVar1;
    puVar2 = puVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  *(uint *)PTR_DAT_000004fc = *(uint *)PTR_DAT_000004fc & 0xfffffff7;
  if (*(int *)PTR_DAT_00000514 != DAT_00000518) {
    check_header();
    return;
  }
  blit_glyphs();
  blit_glyphs();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}
