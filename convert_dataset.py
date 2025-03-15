"""
Script para converter o dataset para outros formatos.
"""

import json
import csv
import os
import argparse

def load_jsonl(file_path):
    """
    Carrega um arquivo JSONL.
    
    Args:
        file_path: Caminho para o arquivo JSONL
    
    Returns:
        list: Lista de objetos JSON
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def save_json(data, file_path):
    """
    Salva dados em formato JSON.
    
    Args:
        data: Dados a serem salvos
        file_path: Caminho para o arquivo de saída
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Dataset salvo em formato JSON: {file_path}")

def save_csv(data, file_path):
    """
    Salva dados em formato CSV.
    
    Args:
        data: Dados a serem salvos
        file_path: Caminho para o arquivo de saída
    """
    if not data:
        print("Erro: Nenhum dado para salvar.")
        return
    
    # Obtém os campos do primeiro exemplo
    fields = list(data[0].keys())
    
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Dataset salvo em formato CSV: {file_path}")

def save_txt(data, output_dir):
    """
    Salva cada exemplo em um arquivo de texto separado.
    
    Args:
        data: Dados a serem salvos
        output_dir: Diretório de saída
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for i, example in enumerate(data):
        file_path = os.path.join(output_dir, f"exemplo_{i+1}.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"MEMÓRIA:\n{example.get('memory', '')}\n\n")
            f.write(f"INPUT DO USUÁRIO:\n{example.get('user_input', '')}\n\n")
            f.write(f"OUTPUT DO ASSISTENTE:\n{example.get('output', '')}\n")
    
    print(f"Dataset salvo em formato TXT: {output_dir}")

def convert_dataset(input_file, output_format, output_path=None):
    """
    Converte o dataset para o formato especificado.
    
    Args:
        input_file: Caminho para o arquivo de entrada (JSONL)
        output_format: Formato de saída (json, csv, txt)
        output_path: Caminho para o arquivo/diretório de saída
    """
    # Carrega o dataset
    try:
        data = load_jsonl(input_file)
        print(f"Dataset carregado: {len(data)} exemplos")
    except Exception as e:
        print(f"Erro ao carregar o dataset: {e}")
        return
    
    # Define o caminho de saída padrão se não for especificado
    if not output_path:
        if output_format == 'json':
            output_path = 'dataset.json'
        elif output_format == 'csv':
            output_path = 'dataset.csv'
        elif output_format == 'txt':
            output_path = 'exemplos_txt'
    
    # Converte para o formato especificado
    if output_format == 'json':
        save_json(data, output_path)
    elif output_format == 'csv':
        save_csv(data, output_path)
    elif output_format == 'txt':
        save_txt(data, output_path)
    else:
        print(f"Formato de saída não suportado: {output_format}")

def main():
    parser = argparse.ArgumentParser(description='Converte o dataset para outros formatos.')
    parser.add_argument('--input', default='dataset.jsonl', help='Caminho para o arquivo de entrada (JSONL)')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json', help='Formato de saída')
    parser.add_argument('--output', help='Caminho para o arquivo/diretório de saída')
    
    args = parser.parse_args()
    
    convert_dataset(args.input, args.format, args.output)

if __name__ == "__main__":
    main() 