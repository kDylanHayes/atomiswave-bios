/* 0000097c  poll_bit  bytes=24 */
void poll_bit(void)
{
  int in_r0;
  do {
    do {
    } while ((*(uint *)PTR_DAT_00000994 & (uint)PTR_DAT_00000998) != 0);
    do {
    } while ((*(uint *)PTR_DAT_00000994 & (uint)PTR_DAT_00000998) == 0);
    in_r0 = in_r0 + -1;
  } while (in_r0 != 0);
  return;
}
