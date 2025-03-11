import json
import os

def salvar_conversa(conversa, arquivo):
    """
    Salva a conversa em um arquivo JSON.
    """
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(arquivo), exist_ok=True)
    
    # Salva o arquivo
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(conversa, f, ensure_ascii=False, indent=2)
    
    # Verifica se o arquivo foi criado
    if not os.path.exists(arquivo):
        raise Exception(f"Erro: O arquivo {arquivo} não foi criado.")