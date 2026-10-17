/* 0000046c  copy_words  bytes=24 */
void copy_words(undefined4 *param_1,int param_2,int param_3)
{
  undefined4 uVar1;
  int in_r2;
  undefined4 *in_r3;
  undefined4 *puVar2;
  int iVar3;
  do {
    param_1 = (undefined4 *)((int)param_1 + in_r2);
    puVar2 = param_1;
    iVar3 = param_2;
    do {
      uVar1 = *in_r3;
      in_r3 = in_r3 + 1;
      *puVar2 = uVar1;
      puVar2 = puVar2 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    param_3 = param_3 + -1;
  } while (param_3 != 0);
  return;
}
