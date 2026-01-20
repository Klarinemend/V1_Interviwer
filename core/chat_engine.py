from google.genai import types

class ChatEngine:

    def __init__(self, model, system_instruction, client_factory):
        self.model = model
        self.system_instruction = system_instruction
        self.client_factory = client_factory

    def gerar_resposta(self, messages, prompt):
        # 1. Detecta pedido de relatório
        termos_relatorio = [
            "gerar relatorio",
            "gerar relatório",
            "relatório final",
            "resumo completo",
            "documentação"
        ]

        eh_relatorio = any(t in prompt.lower() for t in termos_relatorio)

        # 2. Seleciona histórico
        if eh_relatorio:
            msgs_para_contexto = messages[:-1]
        else:
            JANELA = 10
            if len(messages) > JANELA:
                msgs_para_contexto = messages[-(JANELA + 1):-1]
            else:
                msgs_para_contexto = messages[:-1]

        # 3. Converte para formato da API
        api_history = []
        for msg in msgs_para_contexto:
            role = "user" if msg["role"] == "user" else "model"
            api_history.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )

        # 4. Cria client (rotação de chave)
        client = self.client_factory()
        if not client:
            raise Exception("Cliente Gemini não configurado")

        # 5. Cria chat
        chat = client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7
            ),
            history=api_history
        )

        # 6. Envia prompt
        response = chat.send_message(prompt)
        return response.text
