/* 00000350  init_memory  bytes=126 */
void init_memory(void)
{
  undefined *puVar1;
  undefined4 uVar2;
  undefined *puVar3;
  undefined4 *puVar4;
  code *extraout_r1;
  code *extraout_r1_00;
  int iVar5;
  *(undefined4 *)PTR_DAT_000003a0 = DAT_000003a4;
  *(undefined4 *)PTR_DAT_000003a8 = DAT_000003ac;
  *(undefined **)PTR_DAT_000003b0 = PTR_DAT_000003b4;
  uVar2 = DAT_000003bc;
  puVar1 = PTR_DAT_000003b8;
  *(undefined4 *)PTR_DAT_000003b8 = DAT_000003bc;
  *(undefined4 *)(puVar1 + 4) = uVar2;
  puVar1 = PTR_DAT_000003c0;
  *(undefined **)PTR_DAT_000003c0 = PTR_DAT_000003c4;
  *(undefined4 *)(puVar1 + 4) = DAT_000003c8;
  *(undefined4 *)(puVar1 + 8) = 1;
  *(undefined4 *)(puVar1 + 0x10) = 1;
  *(uint *)(puVar1 + 0x14) = 1;
  puVar3 = PTR_DAT_00000428;
  do {
  } while ((*(uint *)(puVar1 + 0x14) & 1) != 0);
  if ((*DAT_000003cc & 3) == 0) {
    check_header();
    return;
  }
  *(undefined4 *)PTR_DAT_00000428 = 0;
  *(undefined4 *)(puVar3 + 4) = 0x500;
  *(uint *)PTR_DAT_0000042c = *(uint *)PTR_DAT_0000042c & 0xfffffff7 | 8;
  puVar4 = DAT_00000430;
  iVar5 = DAT_00000434;
  do {
    *puVar4 = 0xffffffff;
    puVar4 = puVar4 + 1;
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  (*DAT_00000438)(DAT_00000444,DAT_00000448,DAT_0000044c);
  (*extraout_r1)(DAT_00000454,DAT_00000458,DAT_0000045c);
  (*extraout_r1_00)(DAT_00000464,DAT_00000468,DAT_00000468);
  set_system_bits();
  return;
}
