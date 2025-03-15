"""
Script para executar todos os passos em sequência.
"""

import os
import argparse
import subprocess
import time

def run_command(command, description):
    """
    Executa um comando e exibe o resultado.
    
    Args:
        command: Comando a ser executado
        description: Descrição do comando
    
    Returns:
        int: Código de retorno do comando
    """
    print(f"\n{'='*80}")
    print(f"=== {description}")
    print(f"{'='*80}\n")
    
    print(f"Executando: {' '.join(command)}\n")
    
    start_time = time.time()
    result = subprocess.run(command)
    end_time = time.time()
    
    print(f"\nComando concluído em {end_time - start_time:.2f} segundos.")
    print(f"Código de retorno: {result.returncode}")
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description='Executa todos os passos em sequência.')
    parser.add_argument('--skip-generate', action='store_true', help='Pula a geração do dataset')
    parser.add_argument('--skip-analyze', action='store_true', help='Pula a análise do dataset')
    parser.add_argument('--skip-visualize', action='store_true', help='Pula a visualização do dataset')
    parser.add_argument('--skip-finetune', action='store_true', help='Pula o fine-tuning do modelo')
    parser.add_argument('--num-examples', type=int, default=50, help='Número de exemplos a serem gerados')
    
    args = parser.parse_args()
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        print("Erro: O arquivo .env não existe. Crie-o a partir do arquivo .env.example.")
        return 1
    
    # Gera o dataset
    if not args.skip_generate:
        generate_code = run_command(
            ['python', 'generate_dataset.py'],
            "Gerando dataset"
        )
        
        if generate_code != 0:
            print("Erro ao gerar o dataset. Abortando.")
            return generate_code
    
    # Verifica se o dataset existe
    if not os.path.exists('dataset.jsonl'):
        print("Erro: O arquivo dataset.jsonl não existe. Execute o script generate_dataset.py primeiro.")
        return 1
    
    # Analisa o dataset
    if not args.skip_analyze:
        analyze_code = run_command(
            ['python', 'analyze_dataset.py'],
            "Analisando dataset"
        )
        
        if analyze_code != 0:
            print("Erro ao analisar o dataset. Continuando mesmo assim...")
    
    # Visualiza o dataset
    if not args.skip_visualize:
        print("\n{'='*80}")
        print("=== Visualizando dataset")
        print(f"{'='*80}\n")
        
        print("Para visualizar o dataset, execute o comando:")
        print("python visualize_dataset.py")
        
        visualize = input("\nDeseja visualizar o dataset agora? (s/n): ").lower()
        
        if visualize == 's':
            visualize_code = run_command(
                ['python', 'visualize_dataset.py'],
                "Visualizando dataset"
            )
    
    # Realiza o fine-tuning
    if not args.skip_finetune:
        print("\n{'='*80}")
        print("=== Fine-tuning do modelo")
        print(f"{'='*80}\n")
        
        print("O fine-tuning do modelo Qwen2.5:3B requer uma GPU com pelo menos 16GB de VRAM.")
        print("Para GPUs com menos memória, considere usar técnicas como LoRA ou QLoRA.")
        
        finetune = input("\nDeseja realizar o fine-tuning agora? (s/n): ").lower()
        
        if finetune == 's':
            finetune_code = run_command(
                ['python', 'finetune_example.py'],
                "Realizando fine-tuning"
            )
            
            if finetune_code != 0:
                print("Erro ao realizar o fine-tuning. Abortando.")
                return finetune_code
            
            # Testa o modelo
            print("\n{'='*80}")
            print("=== Testando o modelo")
            print(f"{'='*80}\n")
            
            test = input("\nDeseja testar o modelo agora? (s/n): ").lower()
            
            if test == 's':
                test_code = run_command(
                    ['python', 'test_model.py'],
                    "Testando o modelo"
                )
    
    print("\n{'='*80}")
    print("=== Processo concluído com sucesso!")
    print(f"{'='*80}\n")
    
    return 0

if __name__ == "__main__":
    exit(main()) 