/* 00000318  mix_shifts  bytes=40 */
uint mix_shifts(void)
{
  uint in_r0;
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  if ((int)DAT_00000340 < 0) {
    uVar1 = in_r0 >> (~DAT_00000340 & 0x1f) + 1;
  }
  else {
    uVar1 = in_r0 << (DAT_00000340 & 0x1f);
  }
  if ((int)DAT_00000344 < 0) {
    uVar2 = in_r0 >> (~DAT_00000344 & 0x1f) + 1;
  }
  else {
    uVar2 = in_r0 << (DAT_00000344 & 0x1f);
  }
  if ((int)DAT_00000348 < 0) {
    uVar3 = in_r0 >> (~DAT_00000348 & 0x1f) + 1;
  }
  else {
    uVar3 = in_r0 << (DAT_00000348 & 0x1f);
  }
  if ((int)DAT_0000034c < 0) {
    uVar4 = in_r0 >> (~DAT_0000034c & 0x1f) + 1;
  }
  else {
    uVar4 = in_r0 << (DAT_0000034c & 0x1f);
  }
  return (in_r0 ^ uVar1 ^ uVar2 ^ uVar3 ^ 1) & DAT_0000034c | uVar4;
}
