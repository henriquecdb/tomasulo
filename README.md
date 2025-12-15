# Simulador do Algoritmo de Tomasulo

## Descrição

Simulador simples do algoritmo de Tomasulo com interface gráfica em Tkinter para execução de instruções de ponto flutuante.

### Executar o simulador

```bash
python3.12 tomasulo_simulator.py
```

## Funcionalidades

### Modelo de Máquina

- **Registradores**: F0 a F7 (32 bits de ponto flutuante)
- **Memória**: Endereçamento absoluto MEM[endereço]
- **Reservation Stations**:
  - 3 para ADD/SUB (Add1, Add2, Add3)
  - 2 para MUL/DIV (Mul1, Mul2)
  - 2 para LOAD/STORE (Load1, Load2)

### Instruções Suportadas

- **LDF Fd, [addr]**: Carrega float da memória
- **SDF Fs, [addr]**: Armazena float na memória
- **ADDF Fd, Fa, Fb**: Soma de floats
- **SUBF Fd, Fa, Fb**: Subtração de floats
- **MULF Fd, Fa, Fb**: Multiplicação de floats
- **DIVF Fd, Fa, Fb**: Divisão de floats

### Latências de Execução

- LDF, SDF: 2 ciclos
- ADDF, SUBF: 3 ciclos
- MULF: 5 ciclos
- DIVF: 10 ciclos

## Interface Gráfica

### Entrada de Programa

- Digite o código diretamente na caixa de texto
- Carregue um arquivo .txt com o programa
- Formato: uma instrução por linha
- Comentários com `;` são suportados

### Controles

- **Carregar Programa**: Carrega o programa digitado
- **Carregar Arquivo**: Abre um arquivo .txt
- **Próximo Ciclo**: Avança 1 ciclo da simulação
- **Executar Tudo**: Executa até o final
- **Reset**: Reinicia o simulador

### Visualização (Abas)

#### 1. Instruções

Mostra todas as instruções com seus tempos:

- Issue: Ciclo de emissão
- Start Exec: Início da execução
- End Exec: Fim da execução
- Write Result: Ciclo de escrita do resultado
- RS: Reservation Station alocada

#### 2. Reservation Stations

Exibe o estado de cada RS:

- Busy: Se está ocupada
- Op: Operação sendo executada
- Vj, Vk: Valores dos operandos
- Qj, Qk: RS produtoras dos operandos (se aguardando)
- Ciclos: Ciclos restantes de execução

#### 3. Registradores

Lista os registradores F0-F7 com:

- Valor atual
- Status (Qi): Qual RS produzirá o próximo valor

#### 4. Memória

Mostra os endereços de memória acessados e seus valores

## Exemplos de Programas

### Teste 1 - Básico

```
LDF F1, [50]
LDF F2, [51]
LDF F3, [52]
ADDF F4, F1, F2
MULF F5, F4, F3
SDF F5, [53]
```

### Teste 2 - Dependências

```
LDF F1, [75]
LDF F2, [76]
ADDF F3, F1, F2
MULF F4, F3, F1
SUBF F5, F4, F2
DIVF F6, F5, F1
SDF F6, [77]
```

### Teste 3 - Paralelismo

```
LDF F1, [100]
LDF F2, [101]
LDF F3, [102]
LDF F4, [103]
ADDF F5, F1, F2
MULF F6, F3, F4
ADDF F7, F5, F6
SDF F7, [104]
```

## Algoritmo de Tomasulo

O simulador implementa as três fases:

### 1. Issue (Emissão)

- Verifica se há RS livre
- Aloca a instrução
- Verifica disponibilidade dos operandos
- Atualiza register status

### 2. Execute (Execução)

- Aguarda operandos ficarem prontos
- Executa por um número fixo de ciclos
- Calcula o resultado

### 3. Write Result (Escrita)

- Escreve o resultado no registrador/memória
- Atualiza outras RS que dependem deste resultado
- Libera a RS

## Observações

- Memória inicializada com 0.0 por padrão
- Registradores inicializados com 0.0 por padrão
- Valores podem ser configurados antes de carregar o programa
- Endereços são inteiros absolutos
- Apenas operações de ponto flutuante
