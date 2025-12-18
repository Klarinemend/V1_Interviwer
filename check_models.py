import os
import tomllib
from google import genai

def main():
    # 1. Carrega a chave
    secret_path = ".streamlit/secrets.toml"
    
    if not os.path.exists(secret_path):
        print(f"❌ Erro: Arquivo não encontrado em '{secret_path}'")
        return

    try:
        with open(secret_path, "rb") as f:
            secrets = tomllib.load(f)
            api_key = secrets.get("GEMINI_API_KEY")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return

    # 2. Conecta
    print("🔄 Conectando aos servidores do Google...")
    client = genai.Client(api_key=api_key)

    try:
        # 3. Lista os modelos
        print("\n🔎 --- MODELOS GEMINI DISPONÍVEIS ---")
        
        # Pega todos os modelos
        pager = client.models.list()
        
        count = 0
        for m in pager:
            # Filtro simples: se tem 'gemini' no nome, a gente mostra
            if "gemini" in m.name.lower():
                # O ID costuma vir como "models/gemini-1.5-flash", pegamos só o final
                model_id = m.name.split("/")[-1]
                
                print(f"\n🔹 ID:   {model_id}")
                print(f"   Nome: {m.display_name}")
                count += 1

        if count == 0:
            print("\n⚠️ Nenhum modelo Gemini encontrado.")
        else:
            print(f"\n✅ Total listado: {count}")

    except Exception as e:
        print(f"\n❌ Erro ao listar: {e}")

if __name__ == "__main__":
    main()