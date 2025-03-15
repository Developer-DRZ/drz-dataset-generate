"""
Script para visualizar exemplos do dataset de forma interativa.
"""

import json
import os
import random
import argparse
from colorama import init, Fore, Style

# Inicializa o colorama
init()

def load_jsonl(file_path):
    """
    Carrega um arquivo JSONL.
    
    Args:
        file_path: Caminho para o arquivo JSONL
    
    Returns:
        list: Lista de objetos JSON
    """
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo {file_path} não existe.")
        return []
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                print(f"Erro ao decodificar linha: {line}")
    
    return data

def print_colored(text, color=Fore.WHITE, bold=False):
    """
    Imprime texto colorido.
    
    Args:
        text: Texto a ser impresso
        color: Cor do texto
        bold: Se o texto deve ser em negrito
    """
    if bold:
        print(f"{color}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    else:
        print(f"{color}{text}{Style.RESET_ALL}")

def print_example(example, index=None):
    """
    Imprime um exemplo do dataset de forma formatada.
    
    Args:
        example: Exemplo a ser impresso
        index: Índice do exemplo (opcional)
    """
    if index is not None:
        print_colored(f"\n=== Exemplo {index+1} ===", Fore.CYAN, bold=True)
    else:
        print_colored("\n=== Exemplo ===", Fore.CYAN, bold=True)
    
    # Imprime a memória
    print_colored("\nMEMÓRIA:", Fore.YELLOW, bold=True)
    memory_lines = example.get("memory", "").split("\n")
    for line in memory_lines:
        if line.startswith("USER:"):
            print_colored(line, Fore.GREEN)
        elif line.startswith("ASSISTANT:"):
            print_colored(line, Fore.BLUE)
        else:
            print(line)
    
    # Imprime o input do usuário
    print_colored("\nINPUT DO USUÁRIO:", Fore.YELLOW, bold=True)
    print_colored(example.get("user_input", ""), Fore.GREEN)
    
    # Imprime o output do assistente
    print_colored("\nOUTPUT DO ASSISTENTE:", Fore.YELLOW, bold=True)
    
    output = example.get("output", "")
    
    # Divide o output em componentes
    components = [
        ("Input:", Fore.BLUE),
        ("Thought:", Fore.MAGENTA),
        ("ActionInput:", Fore.CYAN),
        ("NextAgent:", Fore.RED),
        ("FinalResponse:", Fore.GREEN)
    ]
    
    current_pos = 0
    for component, color in components:
        if component in output[current_pos:]:
            component_pos = output.find(component, current_pos)
            next_component_pos = len(output)
            
            for next_component, _ in components:
                if next_component != component and next_component in output[component_pos + len(component):]:
                    next_pos = output.find(next_component, component_pos + len(component))
                    if next_pos < next_component_pos:
                        next_component_pos = next_pos
            
            print_colored(component, color, bold=True)
            component_content = output[component_pos + len(component):next_component_pos].strip()
            
            # Formata o ActionInput como JSON se possível
            if component == "ActionInput:":
                try:
                    json_obj = json.loads(component_content)
                    component_content = json.dumps(json_obj, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    pass
            
            print_colored(component_content, color)
            current_pos = next_component_pos

def interactive_viewer(examples):
    """
    Visualizador interativo de exemplos.
    
    Args:
        examples: Lista de exemplos do dataset
    """
    if not examples:
        print("Nenhum exemplo para visualizar.")
        return
    
    num_examples = len(examples)
    current_index = 0
    
    while True:
        # Limpa a tela
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Imprime o exemplo atual
        print_example(examples[current_index], current_index)
        
        # Imprime o menu
        print_colored(f"\n--- Exemplo {current_index+1} de {num_examples} ---", Fore.CYAN)
        print_colored("\nComandos:", Fore.YELLOW)
        print("  n: Próximo exemplo")
        print("  p: Exemplo anterior")
        print("  r: Exemplo aleatório")
        print("  q: Sair")
        
        # Obtém o comando do usuário
        command = input("\nComando: ").lower()
        
        if command == 'n':
            current_index = (current_index + 1) % num_examples
        elif command == 'p':
            current_index = (current_index - 1) % num_examples
        elif command == 'r':
            current_index = random.randint(0, num_examples - 1)
        elif command == 'q':
            break
        else:
            print("Comando inválido.")
            input("Pressione Enter para continuar...")

def main():
    parser = argparse.ArgumentParser(description='Visualiza exemplos do dataset de forma interativa.')
    parser.add_argument('--input', default='dataset.jsonl', help='Caminho para o arquivo de entrada (JSONL)')
    
    args = parser.parse_args()
    
    # Carrega o dataset
    examples = load_jsonl(args.input)
    
    if examples:
        print(f"Dataset carregado: {len(examples)} exemplos")
        interactive_viewer(examples)
    else:
        print("Nenhum exemplo carregado.")

if __name__ == "__main__":
    main() 