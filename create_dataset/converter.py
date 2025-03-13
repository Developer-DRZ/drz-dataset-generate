import json
import sys
import os

def convert_json_to_jsonl(input_file, output_file):
    """
    Convert the JSON format to desired JSONL format
    
    For each turn in the conversation:
    - system value = seller agent's system_prompt
    - human value = buyer agent's resposta
    - gpt value = seller agent's resposta
    """
    try:
        # Read and parse the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.loads(f.read())
        
        # Extract conversations
        conversations = input_data.get("conversa", [])
        
        # Group conversations by turn
        turns = {}
        for conv in conversations:
            turn = conv.get("turno")
            agent = conv.get("agente")
            
            if turn not in turns:
                turns[turn] = {}
            
            turns[turn][agent] = conv
        
        # Create JSONL format
        jsonl_data = []
        for turn_num, turn_data in sorted(turns.items()):
            buyer = turn_data.get("comprador")
            seller = turn_data.get("vendedor")
            
            if buyer and seller:
                jsonl_obj = {
                    "conversations": [
                        {"from": "system", "value": seller.get("sistema_prompt", "")},
                        {"from": "human", "value": buyer.get("resposta", "")},
                        {"from": "gpt", "value": seller.get("resposta", "")}
                    ],
                    "source": "auto-generated",
                    "score": 5.0
                }
                jsonl_data.append(jsonl_obj)
        
        # Write output file - one JSON object per line
        with open(output_file, 'w', encoding='utf-8') as f:
            for obj in jsonl_data:
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')
        
        return f"Conversion successful! Processed {len(jsonl_data)} conversation turns."
    
    except json.JSONDecodeError as e:
        return f"JSON parsing error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python converter.py <input_json_file> <output_jsonl_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    result = convert_json_to_jsonl(input_file, output_file)
    print(result)