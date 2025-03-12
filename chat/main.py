import os
import json
import random
import time
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
        "valores": [50, 70, 100, 150, 200, 250, 300],  # diferentes orçamentos possíveis
        "intencoes": [
            "Comprar o carro mais completo possível dentro do orçamento",
            "Economizar o máximo possível, mesmo que o carro seja mais básico",
            "Encontrar o melhor custo-benefício",
            "Priorizar segurança e conforto, mesmo que use todo o orçamento",
            "Buscar opções de financiamento com entrada de 30%"
        ]
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
            ("Fiat Pulse", "2024"),
            ("Volkswagen Polo", "2024"),
            ("Chevrolet Onix", "2024"),
            ("Renault Kwid", "2024"),
            ("Nissan Kicks", "2024"),
            ("Ford Territory", "2024")
        ],
        "intencoes": [
            "Comprar o modelo na versão top de linha",
            "Encontrar a versão mais econômica deste modelo",
            "Comparar com modelos similares de outras marcas",
            "Verificar disponibilidade para pronta entrega",
            "Negociar descontos ou bônus na compra à vista"
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
        "marcas": ["Toyota", "Honda", "Volkswagen", "Hyundai", "Jeep", "Fiat", "Chevrolet", "Renault", "Nissan", "Ford", "BMW", "Mercedes-Benz", "Audi"],
        "intencoes": [
            "Encontrar o modelo mais vendido da marca",
            "Conhecer o histórico de confiabilidade da marca",
            "Descobrir o modelo com melhor revenda",
            "Explorar opções de SUVs da marca",
            "Conhecer a política de garantia e revisões da marca"
        ]
    },
    {
        "tipo": "categoria",
        "contexto": """Você procura um carro do tipo {categoria} até R$ {valor} mil.
        
        REGRAS ESPECÍFICAS:
        1. Pergunte sobre modelos desta categoria
        2. Compare opções dentro do orçamento
        3. Explore características específicas da categoria
        """,
        "categorias": ["SUV", "Sedan", "Hatch", "Picape", "SUV compacto", "Crossover", "Minivan", "Esportivo"],
        "valores": [80, 100, 150, 200, 250, 300, 400],
        "intencoes": [
            "Encontrar o modelo mais espaçoso da categoria",
            "Buscar o modelo com menor consumo de combustível",
            "Priorizar tecnologia e conectividade",
            "Focar em segurança para família",
            "Buscar o melhor custo-benefício da categoria"
        ]
    },
    {
        "tipo": "primeira_compra",
        "contexto": """Você está comprando seu primeiro carro.
        Experiência: Primeira compra
        Orçamento: R$ {valor} mil
        
        REGRAS ESPECÍFICAS:
        1. Faça perguntas básicas sobre carros
        2. Demonstre certa insegurança nas escolhas
        3. Pergunte sobre manutenção e custos adicionais
        """,
        "valores": [40, 50, 60, 70, 80],
        "intencoes": [
            "Encontrar um carro fácil de dirigir e manter",
            "Priorizar economia de combustível",
            "Buscar um carro com baixo custo de manutenção",
            "Encontrar um modelo com bom valor de revenda",
            "Priorizar segurança para iniciantes"
        ]
    },
    {
        "tipo": "familia",
        "contexto": """Você precisa de um carro para sua família.
        Tamanho da família: {tamanho} pessoas
        Orçamento: R$ {valor} mil
        
        REGRAS ESPECÍFICAS:
        1. Priorize espaço interno e porta-malas
        2. Pergunte sobre segurança
        3. Explore conforto para viagens longas
        """,
        "tamanhos": [3, 4, 5, 6, 7],
        "valores": [80, 100, 120, 150, 180, 200],
        "intencoes": [
            "Encontrar o carro mais espaçoso possível",
            "Priorizar segurança para crianças",
            "Buscar conforto para viagens longas",
            "Encontrar modelo com melhor custo-benefício para família",
            "Verificar opções com 7 lugares"
        ]
    },
    {
        "tipo": "troca",
        "contexto": """Você quer trocar seu atual {carro_atual} {ano_atual} por um modelo mais novo.
        Orçamento para complemento: R$ {valor} mil
        
        REGRAS ESPECÍFICAS:
        1. Pergunte sobre valor de entrada do seu carro atual
        2. Compare com o modelo que você já possui
        3. Explore vantagens da troca
        """,
        "carros_atuais": [
            ("Honda Fit", "2018"),
            ("Toyota Corolla", "2017"),
            ("Volkswagen Gol", "2019"),
            ("Hyundai HB20", "2016"),
            ("Jeep Renegade", "2018"),
            ("Fiat Argo", "2019"),
            ("Chevrolet Onix", "2017")
        ],
        "valores": [20, 30, 40, 50, 60, 80],
        "intencoes": [
            "Fazer upgrade para um modelo superior",
            "Manter-se na mesma categoria, mas com carro mais novo",
            "Trocar por um modelo com menor consumo",
            "Migrar para um SUV",
            "Buscar um carro com mais tecnologia"
        ]
    },
    {
        "tipo": "uso_especifico",
        "contexto": """Você precisa de um carro para um uso específico: {uso}.
        Orçamento: R$ {valor} mil
        
        REGRAS ESPECÍFICAS:
        1. Faça perguntas focadas neste uso específico
        2. Explore características essenciais para sua necessidade
        3. Compare opções adequadas ao seu caso
        """,
        "usos": [
            "trabalhar como motorista de aplicativo",
            "viagens frequentes na estrada",
            "rodar na cidade com muito trânsito",
            "transportar equipamentos de trabalho",
            "usar em estradas de terra e fazendas",
            "economia máxima no dia a dia"
        ],
        "valores": [60, 80, 100, 120, 150, 180],
        "intencoes": [
            "Encontrar o carro mais econômico possível",
            "Priorizar durabilidade e robustez",
            "Buscar conforto para longas jornadas",
            "Encontrar o melhor custo-benefício para o uso específico",
            "Verificar custo de manutenção a longo prazo"
        ]
    },
    {
        "tipo": "financiamento",
        "contexto": """Você quer financiar um carro com parcelas de até R$ {parcela} mensais.
        Entrada disponível: R$ {entrada} mil
        
        REGRAS ESPECÍFICAS:
        1. Pergunte sobre opções de financiamento
        2. Explore taxas de juros e condições
        3. Compare diferentes prazos
        """,
        "parcelas": [800, 1000, 1200, 1500, 2000, 2500],
        "entradas": [10, 15, 20, 30, 40, 50],
        "intencoes": [
            "Encontrar o melhor carro possível dentro do valor da parcela",
            "Minimizar o valor total pago no financiamento",
            "Entender as diferentes modalidades de financiamento",
            "Verificar possibilidade de financiamento sem entrada",
            "Comparar financiamento direto vs. banco"
        ]
    }
]

# Cache para evitar chamadas repetidas à API
resposta_cache = {}

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

def criar_prompt_com_historico(historico, mensagem_atual, tipo_agente, regras_sistema):
    """
    Cria um prompt formatado com histórico de conversa e a mensagem atual.
    
    Args:
        historico: Lista formatada de mensagens ['User: msg', 'Assistant: resp', ...]
        mensagem_atual: A mensagem mais recente do usuário
        tipo_agente: "comprador" ou "vendedor"
        regras_sistema: Regras específicas para este agente
        
    Returns:
        Prompt formatado com histórico e mensagem atual
    """
    # Template do prompt com histórico
    template = f"""<|AgenteAtual|>{tipo_agente}<|AgenteAtual|>

{regras_sistema}

Use the conversation history to provide context and respond to the user's message.

Conversation History:
{historico}

Latest User Message:
{mensagem_atual}"""

    return template

def gerar_resposta(historico, mensagem_atual, tipo_agente, regras_sistema, temperatura=0.2, max_tokens=None, max_retries=3):
    """
    Gera uma resposta usando o Google Gemini AI com histórico de conversa.
    Implementa retry com backoff exponencial e cache.
    """
    # Formata o histórico conforme a perspectiva do agente
    perspectiva = tipo_agente
    historico_formatado = formatar_historico(historico, perspectiva)
    
    # Cria o prompt com histórico e mensagem atual
    prompt = criar_prompt_com_historico(historico_formatado, mensagem_atual, tipo_agente, regras_sistema)
    
    # Adiciona instruções específicas de formatação, se necessário
    if max_tokens:
        prompt += "\n\nIMPORTANTE: Use no máximo 2 frases curtas na sua resposta."
    
    # Verifica se já temos esta resposta em cache
    cache_key = f"{prompt}_{temperatura}_{max_tokens}"
    if cache_key in resposta_cache:
        print("Usando resposta do cache...")
        return resposta_cache[cache_key]
    
    # Implementa retry com backoff exponencial
    for attempt in range(max_retries):
        try:
            # Adiciona um pequeno delay para evitar atingir limites de taxa
            if attempt > 0:
                delay = 2 ** attempt  # Backoff exponencial: 2, 4, 8 segundos
                print(f"Tentativa {attempt+1}/{max_retries}. Aguardando {delay} segundos...")
                time.sleep(delay)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperatura,
                    candidate_count=1,
                    max_output_tokens=150 if max_tokens else 500
                )
            )
            
            resposta = response.text.strip()
            
            # Armazena no cache
            resposta_cache[cache_key] = resposta
            
            return resposta
            
        except Exception as e:
            print(f"Erro na tentativa {attempt+1}: {str(e)}")
            
            # Se for o último retry, tenta usar o fallback
            if attempt == max_retries - 1:
                return gerar_resposta_fallback(tipo_agente, mensagem_atual)
    
    # Não deveria chegar aqui, mas por segurança
    return gerar_resposta_fallback(tipo_agente, mensagem_atual)

def gerar_resposta_fallback(tipo_agente, mensagem_atual):
    """
    Gera uma resposta de fallback quando a API falha.
    """
    print("Usando gerador de resposta fallback...")
    
    # Respostas pré-definidas para o comprador
    respostas_comprador = [
        "Qual o preço deste modelo?",
        "Quais são as opções de cores disponíveis?",
        "Este carro tem garantia de fábrica?",
        "Qual o consumo médio de combustível?",
        "Quais são os itens de série?",
        "Tem disponibilidade para pronta entrega?",
        "Quais são as condições de financiamento?",
        "Este modelo tem câmbio automático?",
        "Qual a potência do motor?",
        "Vocês aceitam carro na troca?"
    ]
    
    # Respostas pré-definidas para o vendedor
    respostas_vendedor = [
        "O preço deste modelo é R$ 89.990,00 na versão básica.",
        "Temos disponibilidade nas cores prata, preto, branco e vermelho.",
        "Sim, o veículo possui 3 anos de garantia de fábrica.",
        "O consumo médio é de 12 km/l na cidade e 14 km/l na estrada.",
        "Este modelo vem equipado com ar-condicionado, direção elétrica e central multimídia.",
        "Temos unidades disponíveis para pronta entrega nas cores prata e branco.",
        "Oferecemos financiamento em até 60 meses com taxa a partir de 0,99% ao mês.",
        "Sim, aceitamos seu veículo usado como parte do pagamento após avaliação.",
        "O motor tem 130 cavalos de potência e torque de 17,5 kgfm.",
        "A versão top de linha custa R$ 115.990,00 com todos os opcionais."
    ]
    
    # Seleciona uma resposta aleatória com base no tipo de agente
    if tipo_agente == "comprador":
        return random.choice(respostas_comprador)
    else:
        return random.choice(respostas_vendedor)

def gerar_conversa():
    """
    Gera uma conversa entre um comprador e um vendedor.
    """
    # Seleciona um cenário aleatório
    cenario = random.choice(CENARIOS_COMPRA)
    
    # Seleciona uma intenção aleatória para este cenário
    intencao = random.choice(cenario["intencoes"])
    
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
    elif cenario["tipo"] == "categoria":
        categoria = random.choice(cenario["categorias"])
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(categoria=categoria, valor=valor)
    elif cenario["tipo"] == "primeira_compra":
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(valor=valor)
    elif cenario["tipo"] == "familia":
        tamanho = random.choice(cenario["tamanhos"])
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(tamanho=tamanho, valor=valor)
    elif cenario["tipo"] == "troca":
        carro_atual, ano_atual = random.choice(cenario["carros_atuais"])
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(carro_atual=carro_atual, ano_atual=ano_atual, valor=valor)
    elif cenario["tipo"] == "uso_especifico":
        uso = random.choice(cenario["usos"])
        valor = random.choice(cenario["valores"])
        contexto = cenario["contexto"].format(uso=uso, valor=valor)
    elif cenario["tipo"] == "financiamento":
        parcela = random.choice(cenario["parcelas"])
        entrada = random.choice(cenario["entradas"])
        contexto = cenario["contexto"].format(parcela=parcela, entrada=entrada)

    # Define as regras para o comprador
    regras_comprador = f"""Você é um cliente interessado em comprar um carro.
    
    {contexto}
    
    SUA INTENÇÃO PRINCIPAL:
    {intencao}
    
    REGRAS OBRIGATÓRIAS:
    1. Faça APENAS UMA pergunta por vez
    2. Seja direto e objetivo
    3. Use português formal
    4. Mantenha o contexto da conversa
    5. Siga uma sequência lógica de perguntas
    6. Suas perguntas devem refletir sua intenção principal"""
    
    # Define as regras para o vendedor
    regras_vendedor = """Você é um vendedor de carros experiente.
    
    REGRAS OBRIGATÓRIAS:
    1. Forneça SEMPRE informações precisas e valores
    2. Use português formal
    3. Seja objetivo (máximo 2 frases)
    4. Mantenha tom profissional e positivo
    5. NUNCA diga que não tem acesso à informação
    6. Use valores de mercado realistas
    7. Forneça detalhes técnicos quando solicitado"""
    
    # Histórico de conversa completo
    historico_conversa = []
    
    # Número de turnos de conversa
    num_turnos = 6  # Aumentado para 6 turnos conforme solicitado

    print(f"Gerando {num_turnos} turnos de conversa...")
    for turno in range(num_turnos):
        print(f"\nTurno {turno + 1}/{num_turnos}")
        
        # Comprador faz uma pergunta
        print("Gerando pergunta do comprador...")
        if turno == 0:
            # Primeira pergunta mais específica
            mensagem_instrucao = "Faça uma pergunta direta sobre um carro específico que você quer comprar."
            # No primeiro turno, não há histórico
            pergunta = gerar_resposta([], mensagem_instrucao, "comprador", regras_comprador)
        else:
            # Próximas perguntas consideram o histórico da conversa
            mensagem_instrucao = "Faça uma nova pergunta sobre o mesmo assunto, considerando a resposta anterior do vendedor."
            pergunta = gerar_resposta(historico_conversa, mensagem_instrucao, "comprador", regras_comprador)
        
        # Adiciona a pergunta ao histórico
        historico_conversa.append({"role": "comprador", "content": pergunta})
        print(f"Comprador: {pergunta}")

        # Vendedor responde
        print("\nGerando resposta do vendedor...")
        resposta = gerar_resposta(historico_conversa, pergunta, "vendedor", regras_vendedor, max_tokens=True)
        
        # Adiciona a resposta ao histórico
        historico_conversa.append({"role": "vendedor", "content": resposta})
        print(f"Vendedor: {resposta}")

    # Adiciona um delay entre as conversas para evitar atingir limites de taxa
    print("Iniciando geração de conversa...")
    time.sleep(1)

    return historico_conversa, cenario["tipo"], intencao

if __name__ == "__main__":
    # Número de conversas a gerar
    num_conversas = 5  # Reduzido para 5 para evitar atingir limites
    
    # Número de turnos por conversa
    turnos_por_conversa = 4  # Reduzido para 4 para economizar chamadas à API
    
    print(f"Iniciando geração de {num_conversas} conversas com {turnos_por_conversa} turnos cada...")
    
    conversas_geradas = 0
    tentativas = 0
    max_tentativas = 10
    
    while conversas_geradas < num_conversas and tentativas < max_tentativas:
        tentativas += 1
        try:
            print(f"\n--- Gerando conversa {conversas_geradas + 1}/{num_conversas} (tentativa {tentativas}) ---")
            
            # Gera a conversa
            conversa, tipo_cenario, intencao = gerar_conversa()
            
            # Verifica se a conversa tem conteúdo válido
            if len(conversa) < 2 or any("erro" in msg["content"].lower() for msg in conversa):
                print("Conversa inválida ou com erros. Tentando novamente...")
                time.sleep(5)  # Espera 5 segundos antes de tentar novamente
                continue
            
            # Cria um objeto com metadados e a conversa
            dados_completos = {
                "metadados": {
                    "tipo_cenario": tipo_cenario,
                    "intencao": intencao,
                    "id": f"{tipo_cenario}_{conversas_geradas+1}"
                },
                "conversa": conversa
            }
            
            # Salva a conversa
            arquivo_saida = f"data/conversa_{tipo_cenario}_{conversas_geradas+1}.json"
            salvar_conversa(dados_completos, arquivo_saida)
            print(f"\nConversa {conversas_geradas+1} ({tipo_cenario}) gerada e salva em: {arquivo_saida}")
            print(f"Intenção do comprador: {intencao}")
            
            # Incrementa o contador de conversas geradas com sucesso
            conversas_geradas += 1
            
            # Espera entre as conversas para evitar atingir limites de taxa
            if conversas_geradas < num_conversas:
                delay = random.randint(3, 7)  # Delay aleatório entre 3 e 7 segundos
                print(f"Aguardando {delay} segundos antes da próxima conversa...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"Erro ao gerar conversa: {str(e)}")
            print("Aguardando 10 segundos antes de tentar novamente...")
            time.sleep(10)
    
    print(f"\nGeração concluída! {conversas_geradas} conversas geradas com sucesso.")
    if conversas_geradas < num_conversas:
        print(f"Aviso: Apenas {conversas_geradas} de {num_conversas} conversas foram geradas devido a erros ou limites de API.")