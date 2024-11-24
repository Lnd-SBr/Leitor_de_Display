import cv2
import os
import time
from datetime import datetime

# Função para garantir que a pasta não tenha mais do que um número máximo de imagens
def manter_limite_imagens(pasta_imagens, limite=10):
    arquivos = os.listdir(pasta_imagens)
    imagens = [f for f in arquivos if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Se o número de imagens exceder o limite
    if len(imagens) > limite:
        # Ordenar as imagens por data de modificação (mais antiga primeiro)
        imagens.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_imagens, x)))

        # Deletar as imagens mais antigas, mantendo o número de imagens igual ao limite
        imagens_a_deletar = imagens[:-limite]
        for imagem in imagens_a_deletar:
            caminho_imagem = os.path.join(pasta_imagens, imagem)
            os.remove(caminho_imagem)
            print(f"Imagem deletada: {imagem}")

# Função principal
def read_display():
    pasta_imagens = r"C:\Leitor_de_Display\Imagens"  # Caminho da pasta onde as imagens estão armazenadas
    diretorio_historico = r"C:\Leitor_de_Display\Historico"

    # Certificar que a pasta de histórico existe
    if not os.path.exists(diretorio_historico):
        os.makedirs(diretorio_historico)  # Cria a pasta se não existir

    # Definir as coordenadas dos segmentos para cada dígito
    segmentos = {
        'D1': {
            'A': (530, 304),
            'B': (557, 332),
            'C': (557, 390),
            'D': (524, 417),
            'E': (498, 393),
            'F': (498, 332),
            'G': (525, 360),
        },
        'D2': {
            'A': (660, 304),
            'B': (687, 332),
            'C': (687, 390),
            'D': (660, 417),
            'E': (626, 391),
            'F': (626, 330),
            'G': (660, 360),
        },
        'D3': {
            'A': (760, 304),
            'B': (787, 332),
            'C': (787, 390),
            'D': (760, 417),
            'E': (725, 391),
            'F': (725, 330),
            'G': (760, 360),
        }
    }

    print("Iniciando o loop de análise. Pressione 'Q' para encerrar.")

    while True:
        # Garantir que a pasta de imagens não ultrapasse 10 arquivos
        manter_limite_imagens(pasta_imagens, limite=10)

        # Obter todos os arquivos na pasta e filtrar apenas imagens
        arquivos = os.listdir(pasta_imagens)
        imagens = [f for f in arquivos if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not imagens:
            print("Nenhuma imagem encontrada na pasta. Tentando novamente...")
            time.sleep(1)  # Aguardar 1 segundo antes de tentar novamente
            continue

        # Ordenar as imagens por data de modificação (mais recente primeiro)
        imagens.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_imagens, x)), reverse=True)

        # Carregar a imagem mais recente
        imagem_recente = os.path.join(pasta_imagens, imagens[0])
        img = cv2.imread(imagem_recente)

        if img is None:
            print("Erro ao carregar a imagem.")
            time.sleep(1)  # Aguardar antes de tentar novamente
            continue

        # Processar os segmentos e marcar os pontos na imagem
        def processar_segmentos(segmentos):
            # Padrões de segmentos para números de 0 a 9
            padroes_numeros = {
                "1111110": "0",
                "0110000": "1",
                "1101101": "2",
                "1111001": "3",
                "0110011": "4",
                "1011011": "5",
                "1011111": "6",
                "1110000": "7",
                "1111111": "8",
                "1111011": "9",
            }

            resultado = ""
            for digito, coords in segmentos.items():
                pixels = {}
                for segmento, coord in coords.items():
                    color = img[coord[1], coord[0]]  # Leitura do pixel
                    pixels[segmento] = color

                    # Se o pixel estiver claro (soma das intensidades RGB > 200), desenha um círculo
                    if sum(color) > 200:
                        # Marcar os pontos na imagem para visualização apenas nos segmentos acesos
                        cv2.circle(img, coord, 5, (0, 255, 255), -1)  # Círculo amarelo nos pontos acesos

                # Analisar os pixels para determinar se está aceso ou apagado
                numero_digito = ""
                for segmento, cor in pixels.items():
                    if sum(cor) > 200:  # Se a soma das intensidades RGB for alta, o pixel está claro
                        numero_digito += "1"  # Segmento aceso
                    else:
                        numero_digito += "0"  # Segmento apagado

                # Converter o padrão lido para um número
                numero = padroes_numeros.get(numero_digito, "?")  # "?" para padrões desconhecidos
                print(f"{digito} - Segmentos: {numero_digito}, Número: {numero}")
                if len(resultado) == 0:  # Se for o primeiro dígito (da esquerda para a direita)
                    resultado += numero + "."  # Adiciona ponto após o primeiro dígito
                else:
                    resultado += numero

            return resultado

        # Processar os três dígitos
        resultado = processar_segmentos(segmentos)

        # Exibir a imagem com os pontos marcados
        cv2.imshow("Imagem com Pontos Marcados", img)

        # Salvar os dados no arquivo
        now = datetime.now()
        data_atual = now.strftime("%d%m%Y")  # Data no formato DDMMYYYY
        hora_atual = now.strftime("%H:%M:%S")  # Hora no formato HH:MM:SS
        arquivo_nome = os.path.join(diretorio_historico, f"{data_atual}.txt")
        
        with open(arquivo_nome, "a") as f:
            f.write(f"{data_atual};{hora_atual};{resultado}\n")
        
        print(f"Resultado gravado no arquivo: {arquivo_nome}")

        # Aguardar por uma tecla ou continuar após 1 segundo
        key = cv2.waitKey(1000)  # Verifica teclas a cada 1 segundo
        if key == ord('q'):  # Tecla "Q" para encerrar
            print("Encerrando o processamento.")
            break

    cv2.destroyAllWindows()

# Testar a função
read_display()
