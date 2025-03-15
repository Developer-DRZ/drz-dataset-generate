"""
Exemplo de como usar o dataset gerado para o fine-tuning do modelo Qwen2.5:3B.

Este script é apenas um exemplo e deve ser adaptado de acordo com suas necessidades.
Para mais informações sobre o fine-tuning do modelo Qwen2.5:3B, consulte a documentação oficial:
https://huggingface.co/docs/transformers/main/en/model_doc/qwen2
"""

import os
import json
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import torch
from datasets import load_dataset

# Configurações
MODEL_NAME = "Qwen/Qwen2.5-3B"
OUTPUT_DIR = "./qwen2-finetuned"
DATASET_PATH = "dataset.jsonl"
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-5
NUM_EPOCHS = 3
MAX_LENGTH = 1024

def prepare_dataset(tokenizer, dataset_path):
    """
    Prepara o dataset para o fine-tuning.
    
    Args:
        tokenizer: Tokenizer do modelo
        dataset_path: Caminho para o arquivo JSONL do dataset
    
    Returns:
        Dataset processado
    """
    # Carrega o dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    
    # Função para processar os exemplos
    def process_example(example):
        # Cria o prompt no formato esperado pelo modelo
        prompt = f"""You are a specialized AI assistant. Use the conversation history to provide context and respond to the user's message.
Conversation History:
{example['memory']}

Latest User Message:
{example['user_input']}"""
        
        # Tokeniza o prompt e a resposta esperada
        tokenized_prompt = tokenizer(prompt, truncation=True, max_length=MAX_LENGTH)
        tokenized_output = tokenizer(example['output'], truncation=True, max_length=MAX_LENGTH)
        
        # Concatena os tokens do prompt e da resposta
        input_ids = tokenized_prompt["input_ids"] + tokenized_output["input_ids"]
        attention_mask = tokenized_prompt["attention_mask"] + tokenized_output["attention_mask"]
        
        # Cria as labels (para o cálculo da loss)
        labels = [-100] * len(tokenized_prompt["input_ids"]) + tokenized_output["input_ids"]
        
        # Trunca se necessário
        if len(input_ids) > MAX_LENGTH:
            input_ids = input_ids[:MAX_LENGTH]
            attention_mask = attention_mask[:MAX_LENGTH]
            labels = labels[:MAX_LENGTH]
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }
    
    # Aplica a função de processamento ao dataset
    processed_dataset = dataset.map(
        process_example,
        remove_columns=dataset.column_names,
        desc="Processando dataset"
    )
    
    return processed_dataset

def main():
    print(f"Iniciando o fine-tuning do modelo {MODEL_NAME}...")
    
    # Carrega o tokenizer e o modelo
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    
    # Configura o tokenizer
    tokenizer.pad_token = tokenizer.eos_token
    
    # Prepara o dataset
    dataset = prepare_dataset(tokenizer, DATASET_PATH)
    
    # Configura os argumentos de treinamento
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        num_train_epochs=NUM_EPOCHS,
        weight_decay=0.01,
        save_strategy="epoch",
        save_total_limit=2,
        logging_steps=10,
        fp16=True,
        remove_unused_columns=False,
    )
    
    # Cria o data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Cria o trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )
    
    # Inicia o treinamento
    trainer.train()
    
    # Salva o modelo e o tokenizer
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print(f"Fine-tuning concluído! Modelo salvo em {OUTPUT_DIR}")

if __name__ == "__main__":
    main() 