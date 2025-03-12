import os
import json
import random
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

def gerar_resposta(mensagens, temperatura=0.2, max_tokens=None):
    """
    Gera uma resposta usando o Google Gemini AI.
    """
    ultima_mensagem = mensagens[-1]["content"]
    
    prompt = f"""INSTRUÇÕES IMPORTANTES:
    1. Responda APENAS em português do Brasil
    2. Seja direto e objetivo
    3. Use linguagem profissional
    4. Mantenha o contexto da conversa
    5. {' Use no máximo 2 frases curtas' if max_tokens else ''}
    
    REGRAS ADICIONAIS PARA VENDEDOR:
    1. SEMPRE forneça informações técnicas e preços (mesmo que aproximados)
    2. NUNCA diga que não tem acesso à informação
    3. Seja sempre positivo e prestativo
    4. Use valores de mercado realistas
    
    RESPONDA: {ultima_mensagem}"""
    
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

    mensagens_comprador = [
        {"role": "system", "content": f"""Você é um cliente interessado em comprar um carro.
        
        {contexto}
        
        REGRAS OBRIGATÓRIAS:
        1. Faça APENAS UMA pergunta por vez
        2. Seja direto e objetivo
        3. Use português formal
        4. Mantenha o contexto da conversa
        5. Siga uma sequência lógica de perguntas"""}
    ]
    
    mensagens_vendedor = [
        {"role": "system", "content": """Você é um vendedor de carros experiente.
        
        REGRAS OBRIGATÓRIAS:
        1. Forneça SEMPRE informações precisas e valores
        2. Use português formal
        3. Seja objetivo (máximo 2 frases)
        4. Mantenha tom profissional e positivo
        5. NUNCA diga que não tem acesso à informação
        6. Use valores de mercado realistas"""}
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

    return conversa, cenario["tipo"]

if __name__ == "__main__":
    num_conversas = 5  # Número de conversas diferentes para gerar
    
    for i in range(num_conversas):
        conversa, tipo_cenario = gerar_conversa()
        arquivo_saida = f"data/conversa_{tipo_cenario}_{i+1}.json"
        salvar_conversa(conversa, arquivo_saida)
        print(f"\nConversa {i+1} ({tipo_cenario}) gerada e salva em: {arquivo_saida}")