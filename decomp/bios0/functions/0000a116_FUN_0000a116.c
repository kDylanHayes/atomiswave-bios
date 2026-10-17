/* 0000a116  FUN_0000a116  bytes=46 */
void FUN_0000a116(void)
{
  int in_GBR;
  (*(code *)PTR_FUN_0000a1bc)();
  *(undefined **)(in_GBR + 0x234) = PTR_DAT_0000a1c0;
  *(undefined4 *)PTR_DAT_0000a1c4 = 8;
                    /* constant jmp to 0x8c000768 */
  (*(code *)PTR_LAB_0000a1c8)();
  return;
}
