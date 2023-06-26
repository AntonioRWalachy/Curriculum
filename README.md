# Curriculum
Analise de currículos com I.A. 

Lê currículos no formato PDF e analisa usando inteligência artificial.
Gera uma lista de pontuações com critérios estabelecidos pelo usuário.
Similiar a um ATS, porém simplificado.

A capacidade da análise é ligada a capacidade do próprio modelo chat GPT. 
Podem ser feitos pedidos sobre local de residência, tempo de experiência, tecnologias que domina,
empregos anteriores, soft skills, idade, etc.

Exemplo:
  Marcos tem 5 anos de experiência com Java
  João tem 3 anos de Java e 6 de Python

  cada ano de experiência com Java vale 2 pontos;
  cada ano de experiência com Python vale 1 ponto;

  1° João 12 pontos
  2° Marcos 10 pontos

Possíveis melhorias incluem:
  - Economia de dados. Para cada parâmetro a ser analisado no currículo, uma cópia é enviada a API. Este processo pode ser extremamente custoso depedendo da quantidade de caracteres do arquivo.
