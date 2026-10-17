/* 00000400  exc_tlb_miss  bytes=38 */
void exc_tlb_miss(void)
{
  code *in_r1;
  code *extraout_r1;
  code *extraout_r1_00;
  (*in_r1)(DAT_00000444,DAT_00000448,DAT_0000044c);
  (*extraout_r1)(DAT_00000454,DAT_00000458,DAT_0000045c);
  (*extraout_r1_00)(DAT_00000464,DAT_00000468,DAT_00000468);
  set_system_bits();
  return;
}
