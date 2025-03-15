"""
Script para analisar o dataset gerado e verificar se está no formato correto.
"""

import json
import os
import re
from collections import Counter

def load_dataset(dataset_path="dataset.jsonl"):
    """
    Carrega o dataset do arquivo JSONL.
    
    Args:
        dataset_path: Caminho para o arquivo JSONL
    
    Returns:
        list: Lista de exemplos do dataset
    """
    if not os.path.exists(dataset_path):
        print(f"Erro: O arquivo {dataset_path} não existe.")
        return []
    
    examples = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                example = json.loads(line.strip())
                examples.append(example)
            except json.JSONDecodeError:
                print(f"Erro ao decodificar linha: {line}")
    
    return examples

def validate_example(example):
    """
    Valida se um exemplo está no formato correto.
    
    Args:
        example: Exemplo a ser validado
    
    Returns:
        tuple: (válido, mensagem de erro)
    """
    # Verifica se o exemplo tem os campos necessários
    required_fields = ["memory", "user_input", "output"]
    for field in required_fields:
        if field not in example:
            return False, f"Campo obrigatório ausente: {field}"
    
    # Verifica se o output está no formato correto
    output = example["output"]
    
    # Verifica se o output contém todos os componentes necessários
    required_components = ["Input:", "Thought:", "ActionInput:", "NextAgent:", "FinalResponse:"]
    for component in required_components:
        if component not in output:
            return False, f"Componente obrigatório ausente no output: {component}"
    
    # Verifica se o ActionInput é um JSON válido
    action_input_match = re.search(r'ActionInput:(.*?)(?=NextAgent:|$)', output, re.DOTALL)
    if action_input_match:
        action_input = action_input_match.group(1).strip()
        try:
            # Tenta converter para JSON
            json.loads(action_input)
        except json.JSONDecodeError:
            return False, f"ActionInput não é um JSON válido: {action_input}"
    
    return True, ""

def analyze_dataset(examples):
    """
    Analisa o dataset e exibe estatísticas.
    
    Args:
        examples: Lista de exemplos do dataset
    """
    if not examples:
        print("Dataset vazio.")
        return
    
    print(f"Total de exemplos: {len(examples)}")
    
    # Valida cada exemplo
    valid_count = 0
    invalid_examples = []
    
    for i, example in enumerate(examples):
        valid, error_message = validate_example(example)
        if valid:
            valid_count += 1
        else:
            invalid_examples.append((i, error_message))
    
    print(f"Exemplos válidos: {valid_count} ({valid_count/len(examples)*100:.2f}%)")
    print(f"Exemplos inválidos: {len(examples) - valid_count} ({(len(examples) - valid_count)/len(examples)*100:.2f}%)")
    
    if invalid_examples:
        print("\nExemplos inválidos:")
        for i, error_message in invalid_examples[:10]:  # Mostra apenas os 10 primeiros
            print(f"  Exemplo {i+1}: {error_message}")
        
        if len(invalid_examples) > 10:
            print(f"  ... e mais {len(invalid_examples) - 10} exemplos inválidos.")
    
    # Analisa os campos do ActionInput
    print("\nAnálise dos campos do ActionInput:")
    
    action_input_fields = Counter()
    
    for example in examples:
        output = example.get("output", "")
        action_input_match = re.search(r'ActionInput:(.*?)(?=NextAgent:|$)', output, re.DOTALL)
        if action_input_match:
            action_input = action_input_match.group(1).strip()
            try:
                action_input_json = json.loads(action_input)
                for field in action_input_json:
                    action_input_fields[field] += 1
            except json.JSONDecodeError:
                pass
    
    for field, count in action_input_fields.most_common():
        print(f"  {field}: {count} ({count/len(examples)*100:.2f}%)")
    
    # Analisa o tamanho das conversas
    memory_lengths = [len(example.get("memory", "").split("\n")) for example in examples]
    avg_memory_length = sum(memory_lengths) / len(memory_lengths) if memory_lengths else 0
    
    print(f"\nTamanho médio da memória (em linhas): {avg_memory_length:.2f}")
    print(f"Tamanho mínimo da memória (em linhas): {min(memory_lengths) if memory_lengths else 0}")
    print(f"Tamanho máximo da memória (em linhas): {max(memory_lengths) if memory_lengths else 0}")

def main():
    print("Analisando dataset gerado...")
    
    # Carrega o dataset
    examples = load_dataset()
    
    if examples:
        # Analisa o dataset
        analyze_dataset(examples)
    
    print("\nAnálise concluída!")

if __name__ == "__main__":
    main() 