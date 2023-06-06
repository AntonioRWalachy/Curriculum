# NEEDS PIP INSTALL
import openai

class AnalysisAi:
    def generate_response(self, messages):
        # REQUEST PARA API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=2048,
            temperature=0.1
        )
        return [response.choices[0].message.content, response.usage]

    def analyse(self, text, param, api_key):
        try:
            openai.api_key = api_key

            # ESTE É O MODELO QUE MELHOR FUNCIONA PARA OBTER O RESULTADO DESEJADO
            message = [{},{}]
            message[0] = {"role": "system", "content": "Responda apenas número!"}
            message[1] = {"role": "user", "content": "Este é um currículo:\n" + text + '\nAnalise o conteúdo do curriculo e: ' + param + '\nResponda apenas números!'}

            answer = self.generate_response(message)
            print(answer[0]) # RESPOSTA
            print(answer[1]) # CONSUMO

            # FORMATA A RESPOSTA
            answer[0] = self.check_response(answer[0])

            return answer[0], True
        except openai.error.AuthenticationError:
            # CHAVE INCORRETA
            print("erro aut")
            return False, False
        except:
            # CASO UMA REQUEST FALHE
            print("erro request")
            return False, True
        
    def check_response(self, response):
        formated_resp = ""
        append_num = True
        for letter in response:
            # RETORNA APENAS A PRIMEIRA SEQUÊNCIA DE NÚMEROS
            # POR EXEMPLO, SE A RESPOSTA FOR: 20 (5 x 4 = 20), RETORNE APENAS 20
            # CASO CONTRÁRIO, A PONTUAÇÃO RETORNADA SERIA 205420
            if letter.isnumeric():
                formated_resp += letter
                append_num = False
            else:
                # QUEBRA APÓS A PRIMEIRA SEQUÊNCIA DE NÚMEROS
                if append_num == False:
                    break
        
        # AS VEZES A AI RETORNA UMA EXPLICAÇÃO DIZENDO QUE NÃO HÁ INFORMAÇÕES SUFICIENTES
        if formated_resp.isnumeric() == False:
            formated_resp = "0"

        return formated_resp

if __name__ == "__main__":
    gpt = AnalysisAi()