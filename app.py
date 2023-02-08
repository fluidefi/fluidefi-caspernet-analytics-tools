from cspr_summarization_block.entities.block import Block
from manage import init_django


for it in Block.objects.all():
  print(it)