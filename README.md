 Projeto Connect Four com MCTS e ID3
 
 1. Objetivos do Trabalho
 Implementar agentes inteligentes para jogar Connect Four usando Monte Carlo Tree Search (MCTS) e
 árvores de decisão (ID3).
 Adicionalmente, treinar e avaliar o algoritmo ID3 sobre o dataset clássico Iris.
 
 2. Implementações- MCTS com UCB1, simulação, expansão e retropropagação.
 3. - Geração de dataset (estado, jogada) com MCTS.
    - Algoritmo ID3 implementado do zero, com cálculo de entropia e ganho de informação.
 4. - Discretização dos atributos do dataset Iris para aplicar ID3.
    - Integração do ID3 ao modo de jogo IA vs IA.
 5. Avaliação e Resultados- Acurácia da árvore ID3 no dataset Iris: 98.00%
 6. - Acurácia da árvore ID3 treinada com dados do MCTS: 93.17%
    - Simulação de 5 jogos entre MCTS (X) e ID3 (O):
  Configuração da Árvore        | Vitórias MCTS (X) | Vitórias ID3 (O) | Empates
  ----------------------------- | ----------------- | ---------------- | ------
  ID3 não podada                | 4                 | 1                | 0
  
  
  ID3 podada (profundidade 4)   | 1                 | 0                | 0
 
 4. Conclusão
 O agente MCTS mostrou-se mais robusto e exploratório, enquanto o ID3 foi eficiente e rápido nas previsões.
 A árvore ID3 obteve boa precisão mesmo com dados complexos, o que mostra sua capacidade de aprender
 padrões de jogo.
 Contudo, observou-se que a versão não podada da árvore ID3 teve desempenho superior no jogo, vencendo
 uma partida.
 Já a versão podada (profundidade 4), apesar de mais interpretável, não conseguiu vencer o MCTS.

