import os
import json
import random
from openai import OpenAI
from utils import salvar_conversa
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada. Verifique se o arquivo .env existe e contém a chave.")

# Inicializa o cliente OpenAI
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    raise Exception(f"Erro ao configurar o cliente OpenAI: {str(e)}")

# Cria o diretório 'data' se não existir
os.makedirs('data', exist_ok=True)

# Templates de cenários de compra
CENARIOS_COMPRA = [
    {
        "tipo": "orcamento",
        "contexto": """Você é um cliente com um orçamento específico.
        Orçamento: R$ {valor} mil
        
        REGRAS ESPECÍFICAS:
        1. Faça perguntas sobre carros dentro do seu orçamento
        2. Explore opções de diferentes marcas
        3. Pergunte sobre condições de financiamento
        """,
        "valores": [50, 70, 100, 150, 200]  # diferentes orçamentos possíveis
    },
    {
        "tipo": "carro_especifico",
        "contexto": """Você está interessado em um {modelo} {ano}.
        
        REGRAS ESPECÍFICAS:
        1. Faça perguntas específicas sobre este modelo
        2. Pergunte sobre versões disponíveis
        3. Explore detalhes técnicos e equipamentos
        """,
        "modelos": [
            ("Honda Civic", "2024"),
            ("Toyota Corolla", "2024"),
            ("Jeep Compass", "2024"),
            ("Hyundai HB20", "2024"),
            ("Fiat Pulse", "2024")
        ]
    },
    {
        "tipo": "marca_especifica",
        "contexto": """Você está interessado em carros da marca {marca}.
        
        REGRAS ESPECÍFICAS:
        1. Pergunte sobre diferentes modelos da marca
        2. Compare versões e preços
        3. Explore diferenciais da marca
        """,
        "marcas": ["Toyota", "Honda", "Volkswagen", "Hyundai", "Jeep"]
    },
    {
        "tipo": "categoria",
        "contexto": """Você procura um carro do tipo {categoria} até R$ {valor} mil.
        
        REGRAS ESPECÍFICAS:
        1. Pergunte sobre modelos desta categoria
        2. Compare opções dentro do orçamento
        3. Explore características específicas da categoria
        """,
        "categorias": ["SUV", "Sedan", "Hatch", "Picape"],
        "valores": [80, 100, 150, 200]
    }
]

def formatar_historico(historico, perspectiva):
    """
    Formata o histórico de conversa com a perspectiva correta (comprador ou vendedor).
    
    Args:
        historico: Lista de mensagens no formato {"role": "comprador"|"vendedor", "content": "mensagem"}
        perspectiva: "comprador" ou "vendedor" - quem está recebendo o histórico
        
    Returns:
        Lista formatada de mensagens como ['User: mensagem', 'Assistant: resposta', ...]
    """
    historico_formatado = []
    
    for msg in historico:
        if perspectiva == "comprador":
            # Para o comprador, o vendedor é o "User" e o comprador é o "Assistant"
            if msg["role"] == "vendedor":
                historico_formatado.append(f"User: {msg['content']}")
            else:
                historico_formatado.append(f"Assistant: {msg['content']}")
        else:  # perspectiva = vendedor
            # Para o vendedor, o comprador é o "User" e o vendedor é o "Assistant"
            if msg["role"] == "comprador":
                historico_formatado.append(f"User: {msg['content']}")
            else:
                historico_formatado.append(f"Assistant: {msg['content']}")
    
    return historico_formatado

def criar_prompt_template(historico, mensagem_atual, tipo_agente):
    """
    Cria o template exato para o prompt do usuário.
    
    Args:
        historico: Lista formatada de mensagens ['User: msg', 'Assistant: resp', ...]
        mensagem_atual: A mensagem mais recente do usuário
        tipo_agente: "comprador" ou "vendedor"
        
    Returns:
        String com o template formatado para o prompt do usuário
    """
    return f"""<|AgenteAtual|>{tipo_agente}<|AgenteAtual|>

You are a specialized AI assistant. Use the conversation history to provide context and respond to the user's message.

Conversation History:
{historico}

Latest User Message:
{mensagem_atual}"""

def gerar_resposta(historico, mensagem_atual, tipo_agente, regras_sistema, temperatura=0.7, max_tokens=None):
    """
    Gera uma resposta usando a API do OpenAI GPT-4o com histórico de conversa.
    
    Args:
        historico: Lista de mensagens no formato {"role": "comprador"|"vendedor", "content": "mensagem"}
        mensagem_atual: A mensagem mais recente do usuário
        tipo_agente: "comprador" ou "vendedor"
        regras_sistema: Regras específicas para este agente
        temperatura: Controla a aleatoriedade das respostas
        max_tokens: Se definido, limita o tamanho da resposta
        
    Returns:
        Tupla (resposta gerada, sistema_prompt, user_prompt)
    """
    # Formata o histórico conforme a perspectiva do agente
    perspectiva = tipo_agente  # O agente que está gerando a resposta
    historico_formatado = formatar_historico(historico, perspectiva)
    
    # Adiciona instrução de tamanho máximo ao sistema, se necessário
    sistema_prompt = regras_sistema
    if max_tokens:
        sistema_prompt += "\n\nIMPORTANTE: Use no máximo 2 frases curtas na sua resposta."
    
    # Cria o prompt do usuário com o template exato
    user_prompt = criar_prompt_template(historico_formatado, mensagem_atual, tipo_agente)
    
    # Prepara os prompts para a API
    try:
        # Chama a API com a estrutura completa de mensagens
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": [{"type": "text", "text": sistema_prompt}]},
                {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
            ],
            response_format={"type": "text"},
            temperature=temperatura,
            max_completion_tokens=150 if max_tokens else 500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip(), sistema_prompt, user_prompt
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        return "Desculpe, houve um erro na geração da resposta.", sistema_prompt, user_prompt

def gerar_conversa():
    """
    Gera uma conversa entre um comprador e um vendedor, mantendo o histórico da conversa.
    """
    # Seleciona um cenário aleatório
    cenario = random.choice(CENARIOS_COMPRA)
    
    # Prepara o contexto específico do cenário
    if cenario["tipo"] == "orcamento":
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(valor=valor)
    elif cenario["tipo"] == "carro_especifico":
        modelo, ano = random.choice(cenario["modelos"])
        contexto = cenario["contexto"].format(modelo=modelo, ano=ano)
    elif cenario["tipo"] == "marca_especifica":
        marca = random.choice(cenario["marcas"])
        contexto = cenario["contexto"].format(marca=marca)
    else:  # categoria
        categoria = random.choice(cenario["categorias"])
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(categoria=categoria, valor=valor)

    # Regras específicas para cada agente (sistema prompts)
    regras_comprador = f"""Você é um cliente interessado em comprar um carro.
    
{contexto}

REGRAS OBRIGATÓRIAS:
1. Faça APENAS UMA pergunta por vez
2. Seja direto e objetivo
3. Use português formal
4. Mantenha o contexto da conversa
5. Siga uma sequência lógica de perguntas"""
    
    regras_vendedor = """Você é um vendedor de carros experiente.

REGRAS OBRIGATÓRIAS:
1. Forneça SEMPRE informações precisas e valores
2. Use português formal
3. Seja objetivo (máximo 2 frases)
4. Mantenha tom profissional e positivo
5. NUNCA diga que não tem acesso à informação
6. Use valores de mercado realistas"""

    # Histórico de conversa completo (apenas mensagens de conteúdo)
    historico_conversa = []
    
    # Histórico completo com prompts e mensagens para salvar
    conversa_completa = []
    
    # Número de turnos de conversa
    num_turnos = 6

    print(f"Gerando {num_turnos} turnos de conversa...")
    for turno in range(num_turnos):
        print(f"\nTurno {turno + 1}/{num_turnos}")
        
        # Comprador faz uma pergunta
        print("Gerando pergunta do comprador...")
        if turno == 0:
            # Primeira pergunta mais específica
            mensagem_instrucao = "Faça uma pergunta direta sobre um carro específico que você quer comprar."
            # No primeiro turno, não há histórico
            pergunta, sistema_comprador, user_prompt_comprador = gerar_resposta(
                [], mensagem_instrucao, "comprador", regras_comprador
            )
        else:
            # Próximas perguntas consideram o histórico da conversa
            mensagem_instrucao = "Faça uma nova pergunta sobre o mesmo assunto, considerando a resposta anterior do vendedor."
            pergunta, sistema_comprador, user_prompt_comprador = gerar_resposta(
                historico_conversa, mensagem_instrucao, "comprador", regras_comprador
            )
        
        # Adiciona a pergunta ao histórico de conversa
        historico_conversa.append({"role": "comprador", "content": pergunta})
        
        # Adiciona todos os detalhes à conversa completa
        conversa_completa.append({
            "turno": turno + 1,
            "agente": "comprador",
            "sistema_prompt": sistema_comprador,
            "user_prompt": user_prompt_comprador,
            "resposta": pergunta
        })
        
        print(f"Comprador: {pergunta}")

        # Vendedor responde
        print("\nGerando resposta do vendedor...")
        resposta, sistema_vendedor, user_prompt_vendedor = gerar_resposta(
            historico_conversa, pergunta, "vendedor", regras_vendedor, max_tokens=True
        )
        
        # Adiciona a resposta ao histórico de conversa
        historico_conversa.append({"role": "vendedor", "content": resposta})
        
        # Adiciona todos os detalhes à conversa completa
        conversa_completa.append({
            "turno": turno + 1,
            "agente": "vendedor",
            "sistema_prompt": sistema_vendedor,
            "user_prompt": user_prompt_vendedor,
            "resposta": resposta
        })
        
        print(f"Vendedor: {resposta}")

    return conversa_completa, cenario["tipo"]

def salvar_conversa_completa(conversa, caminho_arquivo):
    """
    Salva a conversa completa em um arquivo JSON.
    
    Args:
        conversa: Lista completa com prompts e mensagens
        caminho_arquivo: Caminho do arquivo onde a conversa será salva
    """
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(conversa, f, ensure_ascii=False, indent=4)
        print(f"Conversa salva com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar conversa: {str(e)}")

if __name__ == "__main__":
    num_conversas = 5  # Número de conversas diferentes para gerar
    
    for i in range(num_conversas):
        conversa, tipo_cenario = gerar_conversa()
        arquivo_saida = f"data/conversa_{tipo_cenario}_{i+1}.json"
        salvar_conversa_completa(conversa, arquivo_saida)
        print(f"\nConversa {i+1} ({tipo_cenario}) gerada e salva em: {arquivo_saida}")