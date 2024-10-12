import os
import warnings
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
from transformers import TrainingArguments, AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer
from datasets import load_dataset

warnings.filterwarnings('ignore')


def init_model():
    device = 'cuda:0'
    # Do model patching and add fast LoRA weights
    model_name_or_path = "minimind-v1-small"
    tokenizer_name_or_path = "minimind-v1-small"
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, trust_remote_code=True, use_fast=False)
    tokenizer.pad_token = tokenizer.eos_token
    model = model.to(device)
    return model, tokenizer


if __name__ == '__main__':
    model, tokenizer = init_model()
    training_args = TrainingArguments(output_dir="./minimind_dpo",
                                      per_device_train_batch_size=1,
                                      remove_unused_columns=False,
                                      report_to="none")

    dataset_path = './dataset/dpo/train_data.json'
    train_dataset = load_dataset('json', data_files=dataset_path)

    dpo_trainer = DPOTrainer(
        model,
        ref_model=None,
        args=training_args,
        beta=0.1,
        train_dataset=train_dataset['train'],
        tokenizer=tokenizer,
        max_length=512,
        max_prompt_length=512
    )
    dpo_trainer.train()
