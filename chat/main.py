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

<<<<<<< Updated upstream
def gerar_resposta(mensagens, temperatura=0.2, max_tokens=None):
=======
# Cache para evitar chamadas repetidas à API
resposta_cache = {}

# Frases de transição para diferentes cenários
FRASES_TRANSICAO = {
    "orcamento": [
        "Estou procurando um carro dentro do meu orçamento.",
        "Tenho um valor específico para gastar em um carro.",
        "Preciso de um veículo que caiba no meu orçamento.",
        "Estou com um limite de gasto para comprar um carro.",
        "Quero ver opções de carros dentro do valor que posso pagar."
    ],
    "carro_especifico": [
        "Estou interessado em um modelo específico de carro.",
        "Tenho interesse em saber mais sobre este modelo em particular.",
        "Estou procurando informações sobre um carro específico.",
        "Quero conhecer melhor este modelo que me chamou a atenção.",
        "Estou considerando comprar este modelo específico."
    ],
    "marca_especifica": [
        "Tenho preferência por carros desta marca.",
        "Estou procurando opções dentro desta marca específica.",
        "Gostaria de conhecer os modelos disponíveis desta marca.",
        "Tenho interesse particular nesta fabricante de veículos.",
        "Quero explorar o que esta marca tem a oferecer."
    ],
    "categoria": [
        "Estou procurando um veículo desta categoria específica.",
        "Preciso de um carro deste tipo para atender minhas necessidades.",
        "Quero ver opções de veículos nesta categoria.",
        "Estou interessado em carros deste segmento específico.",
        "Gostaria de conhecer modelos disponíveis nesta categoria."
    ],
    "primeira_compra": [
        "Esta será minha primeira compra de um carro.",
        "Nunca comprei um carro antes e preciso de orientação.",
        "Como iniciante, estou procurando meu primeiro veículo.",
        "Sou novo nesse processo de comprar um carro.",
        "Estou comprando meu primeiro carro e tenho algumas dúvidas."
    ],
    "familia": [
        "Preciso de um carro para minha família.",
        "Estou procurando um veículo que acomode toda minha família.",
        "Necessito de um carro espaçoso para uso familiar.",
        "Quero um veículo confortável para viagens em família.",
        "Estou em busca de um carro adequado para minha família."
    ],
    "troca": [
        "Quero trocar meu carro atual por um modelo mais novo.",
        "Estou considerando fazer um upgrade do meu veículo atual.",
        "Gostaria de avaliar a troca do meu carro por outro.",
        "Estou pensando em substituir meu carro atual.",
        "Quero saber as condições para trocar meu veículo."
    ],
    "uso_especifico": [
        "Preciso de um carro para um uso muito específico.",
        "Estou procurando um veículo para uma finalidade particular.",
        "Necessito de um carro que atenda a uma necessidade específica.",
        "Quero um veículo adequado para este uso em particular.",
        "Estou em busca de um carro para uma utilização específica."
    ],
    "financiamento": [
        "Estou interessado em financiar um carro.",
        "Quero conhecer as opções de financiamento disponíveis.",
        "Gostaria de saber sobre as condições de financiamento.",
        "Estou considerando comprar um carro financiado.",
        "Preciso entender melhor como funciona o financiamento de veículos."
    ]
}

# Contextos de conversa para diferentes cenários
CONTEXTOS_CONVERSA = {
    "orcamento": [
        "compra de carro com orçamento limitado",
        "opções de veículos dentro de um valor específico",
        "carros novos e usados dentro do orçamento",
        "melhor custo-benefício para o valor disponível"
    ],
    "carro_especifico": [
        "detalhes técnicos do modelo específico",
        "versões e configurações disponíveis",
        "comparação com concorrentes diretos",
        "avaliações e opiniões sobre o modelo"
    ],
    "marca_especifica": [
        "histórico e reputação da marca",
        "diferenciais dos veículos desta fabricante",
        "política de garantia e assistência técnica",
        "comparação entre diferentes modelos da marca"
    ],
    "categoria": [
        "características típicas desta categoria de veículos",
        "vantagens e desvantagens deste tipo de carro",
        "comparação entre modelos do mesmo segmento",
        "tendências e inovações nesta categoria"
    ],
    "primeira_compra": [
        "dicas para compradores de primeiro carro",
        "aspectos importantes a considerar na primeira compra",
        "documentação e processos para novos proprietários",
        "manutenção básica e cuidados iniciais"
    ],
    "familia": [
        "espaço interno e capacidade de bagagem",
        "itens de segurança para crianças",
        "conforto para viagens longas",
        "economia e praticidade no dia a dia"
    ],
    "troca": [
        "avaliação do veículo usado",
        "vantagens da troca por um modelo mais novo",
        "documentação necessária para transferência",
        "diferenças técnicas entre o modelo atual e o novo"
    ],
    "uso_especifico": [
        "adaptações e características para o uso específico",
        "durabilidade e resistência para a finalidade desejada",
        "consumo e manutenção considerando o uso intensivo",
        "acessórios e equipamentos recomendados"
    ],
    "financiamento": [
        "taxas de juros e condições de pagamento",
        "entrada mínima e valor das parcelas",
        "documentação necessária para aprovação",
        "comparação entre diferentes modalidades de financiamento"
    ]
}

def formatar_historico(historico, perspectiva):
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
if __name__ == "__main__":
    num_conversas = 5  # Número de conversas diferentes para gerar
    
    for i in range(num_conversas):
        conversa, tipo_cenario = gerar_conversa()
        arquivo_saida = f"data/conversa_{tipo_cenario}_{i+1}.json"
        salvar_conversa(conversa, arquivo_saida)
        print(f"\nConversa {i+1} ({tipo_cenario}) gerada e salva em: {arquivo_saida}")
=======
def formatar_dialogo(conversa):
    """
    Formata a conversa no formato de diálogo ["User: pergunta", "Agent: resposta", ...]
    """
    dialogo = []
    for msg in conversa:
        if msg["role"] == "comprador":
            dialogo.append(f"User: {msg['content']}")
        else:
            dialogo.append(f"Agent: {msg['content']}")
    return dialogo

def obter_proximo_id_arquivo():
    """
    Obtém o próximo ID disponível para o arquivo metadata.
    """
    # Lista todos os arquivos metadata existentes
    arquivos = [f for f in os.listdir("data") if f.startswith("metadata") and f.endswith(".json")]
    
    if not arquivos:
        return 1
    
    # Extrai os números dos arquivos existentes
    numeros = []
    for arquivo in arquivos:
        try:
            num = int(arquivo.replace("metadata", "").replace(".json", ""))
            numeros.append(num)
        except ValueError:
            continue
    
    # Retorna o próximo número na sequência
    return max(numeros) + 1 if numeros else 1

def gerar_dataset(num_conversas=5):
    """
    Gera um dataset completo com múltiplas conversas.
    """
    dataset = []
    
    conversas_geradas = 0
    tentativas = 0
    max_tentativas = 15
    
    print(f"Gerando dataset com {num_conversas} conversas...")
    
    while conversas_geradas < num_conversas and tentativas < max_tentativas:
        tentativas += 1
        try:
            print(f"\n--- Gerando conversa {conversas_geradas + 1}/{num_conversas} (tentativa {tentativas}) ---")
            
            # Gera a conversa
            conversa, tipo_cenario, intencao = gerar_conversa()
            
            # Verifica se a conversa tem conteúdo válido
            if len(conversa) < 2 or any("erro" in msg["content"].lower() for msg in conversa):
                print("Conversa inválida ou com erros. Tentando novamente...")
                time.sleep(5)
                continue
            
            # Seleciona uma frase de transição aleatória para este cenário
            frase_transicao = random.choice(FRASES_TRANSICAO[tipo_cenario])
            
            # Seleciona contextos de conversa aleatórios para este cenário
            contextos = random.sample(CONTEXTOS_CONVERSA[tipo_cenario], min(2, len(CONTEXTOS_CONVERSA[tipo_cenario])))
            
            # Formata o diálogo
            dialogo = formatar_dialogo(conversa)
            
            # Cria o objeto de dados para esta conversa
            item_dataset = {
                "id": f"{tipo_cenario}_{conversas_geradas+1}",
                "intent": {
                    "type": tipo_cenario,
                    "description": intencao
                },
                "transition_sentence": {
                    "utterance": frase_transicao,
                    "position": "1"
                },
                "chitchat_context": contextos,
                "dialog": dialogo
            }
            
            # Adiciona ao dataset
            dataset.append(item_dataset)
            
            print(f"Conversa {conversas_geradas+1} ({tipo_cenario}) gerada com sucesso!")
            print(f"Intenção: {intencao}")
            
            # Incrementa o contador de conversas geradas com sucesso
            conversas_geradas += 1
            
            # Espera entre as conversas para evitar atingir limites de taxa
            if conversas_geradas < num_conversas:
                delay = random.randint(3, 7)
                print(f"Aguardando {delay} segundos antes da próxima conversa...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"Erro ao gerar conversa: {str(e)}")
            print("Aguardando 10 segundos antes de tentar novamente...")
            time.sleep(10)
    
    print(f"\nGeração concluída! {conversas_geradas} conversas geradas com sucesso.")
    if conversas_geradas < num_conversas:
        print(f"Aviso: Apenas {conversas_geradas} de {num_conversas} conversas foram geradas devido a erros ou limites de API.")
    
    return dataset

if __name__ == "__main__":
    # Número de conversas a gerar por arquivo
    num_conversas = 5
    
    # Gera o dataset
    dataset = gerar_dataset(num_conversas)
    
    # Obtém o próximo ID disponível para o arquivo
    proximo_id = obter_proximo_id_arquivo()
    
    # Define o nome do arquivo de saída
    arquivo_saida = f"data/metadata{proximo_id}.json"
    
    # Salva o dataset
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\nDataset salvo com sucesso em: {os.path.abspath(arquivo_saida)}")
    print(f"Total de conversas no dataset: {len(dataset)}")
>>>>>>> Stashed changes
