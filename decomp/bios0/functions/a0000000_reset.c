/* a0000000  reset  bytes=54 */
void reset(void)
{
  *DAT_a0000038 = DAT_a000003c;
  *(undefined4 *)PTR_CCR_a0000040 = DAT_a0000044;
  *(undefined **)PTR_DAT_a0000048 = PTR_DAT_a000004c + -1;
                    /* constant jmp to boot at physical 0x5c */
  boot();
  return;
}
