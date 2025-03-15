import json
import os
import random
import google.generativeai as genai
from tqdm import tqdm
import re
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API do Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("A chave de API do Google Gemini não foi encontrada. Certifique-se de configurar a variável de ambiente GOOGLE_API_KEY no arquivo .env")
genai.configure(api_key=GOOGLE_API_KEY)

# Definição de marcas e modelos de carros populares no Brasil
MARCAS = [
    "Volkswagen", "Fiat", "Chevrolet", "Ford", "Toyota", "Honda", "Hyundai", 
    "Renault", "Nissan", "Mitsubishi", "BMW", "Mercedes-Benz", "Audi", 
    "Jeep", "Peugeot", "Citroën", "Kia", "Volvo", "Land Rover", "Subaru"
]

MODELOS = {
    "Volkswagen": ["Gol", "Fox", "Polo", "Golf", "Jetta", "Virtus", "T-Cross", "Tiguan", "Amarok", "Saveiro", "Up", "Voyage"],
    "Fiat": ["Uno", "Palio", "Argo", "Cronos", "Mobi", "Strada", "Toro", "Fiorino", "Doblo", "Pulse", "Fastback"],
    "Chevrolet": ["Onix", "Prisma", "Cruze", "Tracker", "S10", "Spin", "Cobalt", "Montana", "Equinox", "Trailblazer"],
    "Ford": ["Ka", "Fiesta", "Focus", "EcoSport", "Ranger", "Fusion", "Edge", "Mustang", "Territory", "Bronco Sport"],
    "Toyota": ["Corolla", "Yaris", "Etios", "Hilux", "SW4", "RAV4", "Camry", "Prius", "Corolla Cross"],
    "Honda": ["Civic", "Fit", "HR-V", "WR-V", "CR-V", "City", "Accord"],
    "Hyundai": ["HB20", "Creta", "Tucson", "i30", "ix35", "Santa Fe", "Azera", "Elantra"],
    "Renault": ["Kwid", "Sandero", "Logan", "Stepway", "Duster", "Captur", "Oroch", "Master", "Zoe"],
    "Nissan": ["March", "Versa", "Sentra", "Kicks", "Frontier", "Leaf"],
    "Mitsubishi": ["L200", "Pajero", "ASX", "Outlander", "Eclipse Cross"],
    "BMW": ["Série 1", "Série 3", "Série 5", "X1", "X3", "X5", "Z4", "i3"],
    "Mercedes-Benz": ["Classe A", "Classe C", "Classe E", "GLA", "GLC", "GLE", "Sprinter"],
    "Audi": ["A3", "A4", "A5", "Q3", "Q5", "Q7", "TT", "e-tron"],
    "Jeep": ["Renegade", "Compass", "Commander", "Wrangler", "Cherokee"],
    "Peugeot": ["208", "2008", "308", "3008", "408", "5008", "Partner"],
    "Citroën": ["C3", "C4 Cactus", "Aircross", "Jumpy", "Berlingo"],
    "Kia": ["Picanto", "Rio", "Cerato", "Sportage", "Sorento", "Stonic"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "S90", "V60"],
    "Land Rover": ["Discovery", "Discovery Sport", "Range Rover Evoque", "Range Rover Sport", "Range Rover Velar"],
    "Subaru": ["Impreza", "XV", "Forester", "Outback", "WRX"]
}

ESTADOS = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", 
    "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul", 
    "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", 
    "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", 
    "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
]

# Função para gerar um prompt para o Gemini
def generate_prompt(num_turns=3):
    """
    Gera um prompt para o Gemini criar uma conversa de exemplo para o dataset.
    
    Args:
        num_turns: Número de turnos na conversa (padrão: 3)
    
    Returns:
        String contendo o prompt para o Gemini
    """
    # Seleciona uma marca aleatória
    marca = random.choice(MARCAS)
    # Seleciona um modelo aleatório da marca escolhida
    modelo = random.choice(MODELOS[marca])
    # Seleciona um estado aleatório
    estado = random.choice(ESTADOS)
    # Gera um preço aleatório entre R$ 20.000 e R$ 300.000
    preco_min = random.randint(20000, 300000)
    preco_max = preco_min + random.randint(10000, 50000)
    
    # Cria o prompt para o Gemini
    prompt = f"""
    Crie uma conversa em português brasileiro entre um usuário e um assistente virtual chamado Fulano da empresa AutoAvaliar.
    
    A conversa deve ter {num_turns} turnos (um turno = uma mensagem do usuário seguida de uma resposta do assistente).
    
    O usuário está interessado em comprar um carro com as seguintes características (algumas podem não ser mencionadas explicitamente):
    - Marca: {marca}
    - Modelo: {modelo}
    - Estado: {estado}
    - Faixa de preço: Entre R$ {preco_min} e R$ {preco_max}
    
    O assistente deve seguir o seguinte formato de resposta:
    ```
    Input: [O input do usuário]  
    Thought: [Pensamento da LLM sobre o input do usuário]
    ActionInput: [Um JSON object com todos os parâmetros coletados para filtros]
    NextAgent: ListingAgent
    FinalResponse: "Movendo para o próximo agente".
    ```
    
    O ActionInput deve ser um JSON que pode conter os seguintes campos:
    - id
    - title (nome do carro Ex: "Fusca 1970")
    - description (descrição do carro)
    - brand (marca do carro)
    - salePrice (preço de venda do carro)
    - fipePercentage (percentual de fipe do carro)
    - fipePrice (preço de fipe do carro)
    
    O usuário pode não informar alguns campos, portanto esses campos devem ficar com o valor em branco no JSON.
    
    A conversa deve ser natural e realista, com o usuário fornecendo informações gradualmente ao longo da conversa.
    O assistente deve sempre considerar o histórico da conversa (memória) para fornecer respostas mais assertivas.
    
    Forneça a conversa completa no formato:
    
    USER: [mensagem do usuário]
    ASSISTANT: [resposta do assistente no formato especificado]
    USER: [próxima mensagem do usuário]
    ASSISTANT: [próxima resposta do assistente]
    ...
    
    Certifique-se de que o JSON no ActionInput seja válido e esteja formatado corretamente.
    """
    
    return prompt

# Função para processar a resposta do Gemini e extrair as conversas
def process_gemini_response(response_text):
    """
    Processa a resposta do Gemini e extrai as conversas no formato desejado.
    
    Args:
        response_text: Texto da resposta do Gemini
    
    Returns:
        Lista de dicionários contendo as conversas processadas
    """
    # Divide a resposta em turnos de conversa
    turns = re.split(r'USER:|ASSISTANT:', response_text)
    turns = [turn.strip() for turn in turns if turn.strip()]
    
    conversations = []
    memory = ""
    
    for i in range(0, len(turns), 2):
        if i + 1 < len(turns):
            user_message = turns[i].strip()
            assistant_message = turns[i + 1].strip()
            
            # Extrai os componentes da resposta do assistente
            input_match = re.search(r'Input:(.*?)(?=Thought:|$)', assistant_message, re.DOTALL)
            thought_match = re.search(r'Thought:(.*?)(?=ActionInput:|$)', assistant_message, re.DOTALL)
            action_input_match = re.search(r'ActionInput:(.*?)(?=NextAgent:|$)', assistant_message, re.DOTALL)
            next_agent_match = re.search(r'NextAgent:(.*?)(?=FinalResponse:|$)', assistant_message, re.DOTALL)
            final_response_match = re.search(r'FinalResponse:(.*?)(?=$)', assistant_message, re.DOTALL)
            
            # Verifica se todos os componentes foram encontrados
            if input_match and thought_match and action_input_match and next_agent_match and final_response_match:
                input_text = input_match.group(1).strip()
                thought = thought_match.group(1).strip()
                action_input = action_input_match.group(1).strip()
                next_agent = next_agent_match.group(1).strip()
                final_response = final_response_match.group(1).strip()
                
                # Tenta converter o ActionInput para um objeto JSON válido
                try:
                    action_input_json = json.loads(action_input)
                    action_input = json.dumps(action_input_json, ensure_ascii=False)
                except json.JSONDecodeError:
                    # Se não for um JSON válido, tenta limpar e corrigir
                    action_input = action_input.replace("'", '"')
                    try:
                        action_input_json = json.loads(action_input)
                        action_input = json.dumps(action_input_json, ensure_ascii=False)
                    except json.JSONDecodeError:
                        # Se ainda não for válido, mantém como string
                        pass
                
                # Atualiza a memória com a conversa atual
                if memory:
                    memory += f"\nUSER: {user_message}\nASSISTANT: Input: {input_text}\nThought: {thought}\nActionInput: {action_input}\nNextAgent: {next_agent}\nFinalResponse: {final_response}"
                else:
                    memory = f"USER: {user_message}\nASSISTANT: Input: {input_text}\nThought: {thought}\nActionInput: {action_input}\nNextAgent: {next_agent}\nFinalResponse: {final_response}"
                
                # Cria o exemplo para o dataset
                example = {
                    "memory": memory,
                    "user_input": user_message,
                    "output": f"Input: {input_text}\nThought: {thought}\nActionInput: {action_input}\nNextAgent: {next_agent}\nFinalResponse: {final_response}"
                }
                
                conversations.append(example)
    
    return conversations

# Função para gerar o dataset
def generate_dataset(num_examples=50, examples_per_call=2):
    """
    Gera o dataset de treinamento.
    
    Args:
        num_examples: Número total de exemplos a serem gerados
        examples_per_call: Número de exemplos a serem gerados por chamada ao Gemini
    
    Returns:
        Lista de exemplos gerados
    """
    dataset = []
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    num_calls = (num_examples + examples_per_call - 1) // examples_per_call
    
    for _ in tqdm(range(num_calls), desc="Gerando exemplos"):
        try:
            # Gera o prompt
            prompt = generate_prompt(num_turns=random.randint(2, 4))
            
            # Faz a chamada ao Gemini
            response = model.generate_content(prompt)
            
            # Processa a resposta
            examples = process_gemini_response(response.text)
            
            # Adiciona os exemplos ao dataset
            dataset.extend(examples)
            
            # Limita o número de exemplos ao solicitado
            if len(dataset) >= num_examples:
                dataset = dataset[:num_examples]
                break
                
        except Exception as e:
            print(f"Erro ao gerar exemplos: {e}")
    
    return dataset

# Função para salvar o dataset em formato JSONL
def save_jsonl(dataset, filename="dataset.jsonl"):
    """
    Salva o dataset em formato JSONL.
    
    Args:
        dataset: Lista de exemplos
        filename: Nome do arquivo de saída
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for example in dataset:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"Dataset salvo em {filename}")

# Função para salvar exemplos em formato legível
def save_readable_examples(dataset, output_dir="exemplos"):
    """
    Salva os exemplos em formato legível.
    
    Args:
        dataset: Lista de exemplos
        output_dir: Diretório de saída
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for i, example in enumerate(dataset):
        filename = os.path.join(output_dir, f"exemplo_{i+1}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"MEMÓRIA:\n{example['memory']}\n\n")
            f.write(f"INPUT DO USUÁRIO:\n{example['user_input']}\n\n")
            f.write(f"OUTPUT DO ASSISTENTE:\n{example['output']}\n")
    
    print(f"Exemplos legíveis salvos em {output_dir}")

# Função principal
def main():
    print("Iniciando geração do dataset para fine-tuning do modelo Qwen2.5:3B...")
    
    # Gera o dataset
    dataset = generate_dataset(num_examples=50)
    
    # Salva o dataset em formato JSONL
    save_jsonl(dataset)
    
    # Salva os exemplos em formato legível
    save_readable_examples(dataset)
    
    print(f"Geração concluída! Total de {len(dataset)} exemplos gerados.")

if __name__ == "__main__":
    main() 