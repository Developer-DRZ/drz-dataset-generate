import os
import json
import google.generativeai as genai
from utils import salvar_conversa
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada. Verifique se o arquivo .env existe e contém a chave.")

# Configuração do modelo
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    raise Exception(f"Erro ao configurar o modelo Gemini: {str(e)}")

# Cria o diretório 'data' se não existir
os.makedirs('data', exist_ok=True)

def gerar_resposta(mensagens, temperatura=0.2, max_tokens=None):
    """
    Gera uma resposta usando o Google Gemini AI.
    """
    # Converte o formato das mensagens para o texto da última mensagem
    ultima_mensagem = mensagens[-1]["content"]
    
    # Adiciona instrução explícita de idioma e tamanho
    prompt = f"""INSTRUÇÕES IMPORTANTES:
    1. Responda APENAS em português do Brasil
    2. Seja direto e objetivo
    3. NÃO use linguagem informal ou gírias
    4. NÃO faça comentários adicionais
    {' 5. Use no máximo 2 frases curtas' if max_tokens else ''}
    
    RESPONDA: {ultima_mensagem}"""
    
    # Faz a requisição para o Gemini
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperatura,
                candidate_count=1,
                max_output_tokens=150 if max_tokens else 500
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        return "Desculpe, houve um erro na geração da resposta."

def gerar_conversa():
    """
    Gera uma conversa entre um comprador e um vendedor.
    """
    mensagens_comprador = [
        {"role": "system", "content": """Você é um cliente interessado em comprar um carro. 
        
        REGRAS OBRIGATÓRIAS:
        1. Faça APENAS UMA pergunta direta sobre um carro específico
        2. NÃO faça introduções ou comentários
        3. NÃO responda perguntas
        4. Use português formal do Brasil
        5. Mantenha o contexto da conversa anterior
        
        EXEMPLOS DE PERGUNTAS PERMITIDAS:
        - "Qual o preço do Honda Civic 2024 LX?"
        - "O Toyota Corolla XEi tem câmbio automático?"
        - "Qual a garantia do Jeep Compass?"
        
        FORMATO DA SUA RESPOSTA:
        Apenas a pergunta, sem introdução ou comentários."""}
    ]
    
    mensagens_vendedor = [
        {"role": "system", "content": """Você é um vendedor de carros experiente.
        
        REGRAS OBRIGATÓRIAS:
        1. Responda APENAS o que foi perguntado
        2. Use português formal do Brasil
        3. Máximo de 2 frases curtas
        4. NÃO faça perguntas
        5. NÃO use gírias ou emojis
        6. NÃO faça sugestões adicionais
        
        EXEMPLO DE RESPOSTA BOA:
        Pergunta: "Qual o preço do Honda Civic 2024?"
        Resposta: "O Honda Civic 2024 LX custa R$ 244.900,00."
        
        FORMATO DA SUA RESPOSTA:
        Apenas a informação solicitada, sem introdução ou comentários."""}
    ]

    conversa = []
    num_turnos = 3

    print(f"Gerando {num_turnos} turnos de conversa...")
    for turno in range(num_turnos):
        print(f"\nTurno {turno + 1}/{num_turnos}")
        
        # Comprador faz uma pergunta
        print("Gerando pergunta do comprador...")
        if turno == 0:
            # Primeira pergunta mais específica
            mensagens_comprador.append({"role": "user", "content": "Faça uma pergunta direta sobre um carro específico que você quer comprar."})
        else:
            # Próximas perguntas consideram o contexto
            mensagens_comprador.append({"role": "user", "content": "Faça uma nova pergunta sobre o mesmo carro, considerando a resposta anterior do vendedor."})
        
        pergunta = gerar_resposta(mensagens_comprador)
        conversa.append({"role": "comprador", "content": pergunta})
        print(f"Comprador: {pergunta}")

        # Vendedor responde
        print("\nGerando resposta do vendedor...")
        mensagens_vendedor.append({"role": "user", "content": pergunta})
        resposta = gerar_resposta(mensagens_vendedor, max_tokens=True)  # Limita o tamanho da resposta
        conversa.append({"role": "vendedor", "content": resposta})
        print(f"Vendedor: {resposta}")

        # Atualiza o contexto
        mensagens_comprador.append({"role": "assistant", "content": resposta})
        mensagens_vendedor.append({"role": "assistant", "content": resposta})

    return conversa

if __name__ == "__main__":
    conversa = gerar_conversa()
    salvar_conversa(conversa, "data/conversa.json")
    print("\nConversa gerada e salva com sucesso em 'data/conversa.json'!")
    
    # Verifica se o arquivo foi criado
    if os.path.exists("data/conversa.json"):
        print("Arquivo criado com sucesso!")
        # Mostra o conteúdo do arquivo
        with open("data/conversa.json", 'r', encoding='utf-8') as f:
            print("\nConteúdo do arquivo:")
            print(json.dumps(json.load(f), ensure_ascii=False, indent=2))