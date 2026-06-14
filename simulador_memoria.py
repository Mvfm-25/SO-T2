###
###     S I M U L A D O R    D E    M E M Ó R I A
###
### Prof. Filipo - github.com/ProfessorFilipo/MemSim/
###
### Grupo 01 - FIFO (First-In, First-Out) vs. LRU (Least Recently Used)
###

import sys


class Frame:
    def __init__(self, id_frame):
        self.id_frame = id_frame
        self.pagina_alocada = None  # Armazena o número da página ou None se estiver vazio
        # Marca de tempo (relógio lógico) usada pelos algoritmos de substituição:
        #   - FIFO: registra o instante em que a página ENTROU no frame (não muda em hits).
        #   - LRU : registra o instante do ÚLTIMO acesso à página (atualizado também em hits).
        self.timestamp = 0


class TabelaPaginas:
    def __init__(self, num_frames, algoritmo="FIFO"):
        # Inicializa a memória física com a quantidade de frames especificada
        self.frames = [Frame(i) for i in range(num_frames)]
        self.algoritmo = algoritmo.upper()
        self.total_page_faults = 0
        self.total_acessos = 0
        # Relógio lógico: incrementado a cada acesso para gerar marcas de tempo únicas
        self.relogio = 0

    def acessar_pagina(self, numero_pagina):
        self.total_acessos += 1
        self.relogio += 1

        # 1. Verificar se a página já está em algum frame (Hit)
        for frame in self.frames:
            if frame.pagina_alocada == numero_pagina:
                # No LRU o acesso renova a "idade" da página; no FIFO a ordem de
                # entrada é preservada e nada muda em um hit.
                if self.algoritmo == "LRU":
                    frame.timestamp = self.relogio
                return True, frame.id_frame  # Retorna (Hit=True, frame_id)

        # 2. Se não encontrou, ocorreu um Page Fault!
        self.total_page_faults += 1

        # 3. Verificar se existe algum frame vazio disponível
        for frame in self.frames:
            if frame.pagina_alocada is None:
                frame.pagina_alocada = numero_pagina
                frame.timestamp = self.relogio  # registra a entrada da página
                return False, frame.id_frame  # Retorna (Hit=False, frame_id)

        # 4. Memória cheia: Aplicar algoritmo de substituição de página
        frame_vitima_id = self.substituir_pagina(numero_pagina)
        return False, frame_vitima_id

    def substituir_pagina(self, nova_pagina):
        """
        Escolhe a página 'vítima' a ser substituída segundo o algoritmo configurado.

        FIFO e LRU compartilham o mesmo critério de escolha: o frame com a MENOR
        marca de tempo (timestamp). A diferença está em QUANDO o timestamp é
        atualizado (definido em acessar_pagina):
          - FIFO: timestamp só é gravado na entrada da página  -> sai a mais antiga
                  a ENTRAR na memória.
          - LRU : timestamp é gravado também em cada acesso     -> sai a usada há
                  MAIS tempo (menos recentemente usada).
        """
        # Seleciona o frame de menor timestamp (a página mais "velha" pelo critério).
        frame_vitima = min(self.frames, key=lambda frame: frame.timestamp)

        # Substitui a página vítima pela nova e registra o instante da entrada.
        frame_vitima.pagina_alocada = nova_pagina
        frame_vitima.timestamp = self.relogio

        return frame_vitima.id_frame

    def imprimir_mapa_memoria(self, passo, pagina_acessada, foi_hit, frame_alterado=None):
        """
        Imprime o estado atual da memória física (frames) no terminal, seguindo o
        padrão visual exigido no enunciado: cabeçalho do passo com o status do
        acesso, conteúdo de cada frame e marcação do frame alterado.
        """
        status = "Hit" if foi_hit else "Page Fault"
        print(f"\n--- Passo {passo}: Acesso à Página {pagina_acessada} ({status}) ---")

        for frame in self.frames:
            conteudo = f"Página {frame.pagina_alocada}" if frame.pagina_alocada is not None else "[Vazio]"
            marcador = " <-- Alterado" if frame.id_frame == frame_alterado and not foi_hit else ""
            print(f"[Frame {frame.id_frame}]: {conteudo}{marcador}")

        print("-" * 40)


class Simulador:
    def __init__(self, caminho_arquivo, algoritmo="FIFO"):
        self.caminho_arquivo = caminho_arquivo
        self.algoritmo = algoritmo.upper()

    def _ler_entrada(self):
        """Lê o arquivo de entrada e retorna (num_frames, lista_de_paginas).

        O parsing é tolerante ao formato: aceita um número por linha (padrão do
        enunciado), vários números na mesma linha, espaços/tabs extras e
        comentários iniciados por '#' (linha inteira ou no fim da linha). O
        primeiro número encontrado é o total de frames; os demais são as páginas.
        """
        try:
            # utf-8-sig descarta um eventual BOM gravado por editores no Windows.
            with open(self.caminho_arquivo, "r", encoding="utf-8-sig") as arquivo:
                conteudo = arquivo.read()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.caminho_arquivo}' não foi encontrado.")
            return None, None
        except OSError as erro:
            print(f"Erro ao abrir o arquivo '{self.caminho_arquivo}': {erro}")
            return None, None

        # Coleta os tokens numéricos linha a linha, removendo comentários inline (#)
        # e qualquer espaçamento. Funciona tanto para "um número por linha" quanto
        # para sequências separadas por espaços/tabs.
        tokens = []
        for linha in conteudo.splitlines():
            sem_comentario = linha.split("#", 1)[0]
            tokens.extend(sem_comentario.split())

        if not tokens:
            print("Erro: Arquivo de entrada vazio ou sem dados numéricos.")
            return None, None

        try:
            numeros = [int(token) for token in tokens]
        except ValueError:
            print("Erro: O arquivo de entrada deve conter apenas números inteiros.")
            return None, None

        # O primeiro número define a quantidade de frames; o restante são as páginas.
        num_frames, paginas = numeros[0], numeros[1:]

        if num_frames <= 0:
            print("Erro: O número de frames deve ser um inteiro positivo.")
            return None, None

        return num_frames, paginas

    def executar(self):
        num_frames, paginas = self._ler_entrada()
        if num_frames is None:
            return

        tabela_paginas = TabelaPaginas(num_frames, self.algoritmo)

        print(f"\n########## ALGORITMO: {self.algoritmo} ##########")
        print(f"Iniciando simulação com {num_frames} frames disponíveis.")
        print("=" * 40)

        for passo, numero_pagina in enumerate(paginas, start=1):
            # Processa o acesso na tabela de páginas
            foi_hit, frame_id = tabela_paginas.acessar_pagina(numero_pagina)
            # Renderiza o mapa de memória para acompanhar o passo a passo
            tabela_paginas.imprimir_mapa_memoria(passo, numero_pagina, foi_hit, frame_id)

        # Exibição das estatísticas finais da simulação
        print("\n================ STATS FINAIS ================")
        print(f"Total de Acessos: {tabela_paginas.total_acessos}")
        print(f"Total de Page Faults: {tabela_paginas.total_page_faults}")
        if tabela_paginas.total_acessos > 0:
            taxa_faults = (tabela_paginas.total_page_faults / tabela_paginas.total_acessos) * 100
            print(f"Taxa de Page Faults: {taxa_faults:.2f}%")
        print("==============================================")


def main():
    """
    Uso:
        python simulador_memoria.py [arquivo_entrada] [algoritmo]

    - arquivo_entrada: caminho do arquivo (padrão: entrada.txt)
    - algoritmo      : FIFO, LRU ou AMBOS (padrão: AMBOS)

    Exemplos:
        python simulador_memoria.py                  -> entrada.txt, FIFO e LRU
        python simulador_memoria.py entrada.txt FIFO -> apenas FIFO
        python simulador_memoria.py entrada.txt LRU  -> apenas LRU
    """
    arquivo_entrada = sys.argv[1] if len(sys.argv) > 1 else "entrada.txt"
    algoritmo = sys.argv[2].upper() if len(sys.argv) > 2 else "AMBOS"

    algoritmos_validos = {"FIFO", "LRU", "AMBOS"}
    if algoritmo not in algoritmos_validos:
        print(f"Algoritmo '{algoritmo}' inválido. Use FIFO, LRU ou AMBOS.")
        return

    # Grupo 01: comparação entre FIFO e LRU. Por padrão executa os dois.
    algoritmos = ["FIFO", "LRU"] if algoritmo == "AMBOS" else [algoritmo]
    for alg in algoritmos:
        Simulador(arquivo_entrada, alg).executar()


if __name__ == "__main__":
    main()
