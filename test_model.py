"""
Script para testar o modelo Qwen2.5:3B após o fine-tuning.
"""

import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Configurações
MODEL_PATH = "./qwen2-finetuned"  # Caminho para o modelo fine-tuned
MAX_LENGTH = 1024
TEMPERATURE = 0.7
TOP_P = 0.9
TOP_K = 50

def load_model():
    """
    Carrega o modelo e o tokenizer.
    
    Returns:
        tuple: (modelo, tokenizer)
    """
    print(f"Carregando modelo de {MODEL_PATH}...")
    
    # Carrega o tokenizer e o modelo
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    
    return model, tokenizer

def generate_response(model, tokenizer, memory, user_input):
    """
    Gera uma resposta do modelo para o input do usuário.
    
    Args:
        model: Modelo carregado
        tokenizer: Tokenizer carregado
        memory: Histórico da conversa
        user_input: Input do usuário
    
    Returns:
        str: Resposta gerada pelo modelo
    """
    # Cria o prompt no formato esperado pelo modelo
    prompt = f"""You are a specialized AI assistant. Use the conversation history to provide context and respond to the user's message.
Conversation History:
{memory}

Latest User Message:
{user_input}"""
    
    # Tokeniza o prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Gera a resposta
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=MAX_LENGTH,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decodifica a resposta
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove o prompt da resposta
    response = response[len(prompt):].strip()
    
    return response

def interactive_chat():
    """
    Inicia um chat interativo com o modelo.
    """
    model, tokenizer = load_model()
    memory = ""
    
    print("\n=== Chat Interativo com o Modelo Fine-Tuned ===")
    print("Digite 'sair' para encerrar o chat.\n")
    
    while True:
        # Obtém o input do usuário
        user_input = input("Você: ")
        
        if user_input.lower() in ["sair", "exit", "quit"]:
            print("\nEncerrando o chat. Até logo!")
            break
        
        # Gera a resposta
        response = generate_response(model, tokenizer, memory, user_input)
        
        # Exibe a resposta
        print(f"\nFulano: {response}\n")
        
        # Atualiza a memória
        if memory:
            memory += f"\nUSER: {user_input}\nASSISTANT: {response}"
        else:
            memory = f"USER: {user_input}\nASSISTANT: {response}"

def main():
    interactive_chat()

if __name__ == "__main__":
    main() 