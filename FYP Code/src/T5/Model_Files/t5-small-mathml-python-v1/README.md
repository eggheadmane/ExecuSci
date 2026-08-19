---
library_name: peft
license: apache-2.0
base_model: t5-small
tags:
- generated_from_trainer
model-index:
- name: t5-small-mathml-python-v1
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

[<img src="https://raw.githubusercontent.com/wandb/assets/main/wandb-github-badge-28.svg" alt="Visualize in Weights & Biases" width="200" height="32"/>](https://wandb.ai/kj821-imperial-college-london/mathml-python/runs/bkznynip)
[<img src="https://raw.githubusercontent.com/wandb/assets/main/wandb-github-badge-28.svg" alt="Visualize in Weights & Biases" width="200" height="32"/>](https://wandb.ai/kj821-imperial-college-london/mathml-python/runs/bkznynip)
# t5-small-mathml-python-v1

This model is a fine-tuned version of [t5-small](https://huggingface.co/t5-small) on an unknown dataset.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.0001
- train_batch_size: 32
- eval_batch_size: 64
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 3
- mixed_precision_training: Native AMP

### Framework versions

- PEFT 0.15.1
- Transformers 4.45.2
- Pytorch 2.6.0+cu126
- Datasets 2.19.1
- Tokenizers 0.20.1