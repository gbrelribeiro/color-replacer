<h1 align="center">
  Trocador de Cor
</h1>

## ⬇️ Download

| Versão | Download |
|---|---|
| v1.0.0 (Windows) | [**color_replace.exe**](https://github.com/gbrelribeiro/color-replacer/releases/tag/v1.0.0) |

> Não precisa ter Python instalado — só baixar e executar.

Aplicação desktop com interface gráfica que substitui uma cor específica de imagens por outra cor, mantendo a transparência original e salvando o resultado em PNG.

## Descrição

O **Trocador de Cor** é uma ferramenta visual construída com Python e Tkinter que permite escolher uma cor de origem e uma cor de destino (por código HEX ou clicando na imagem) e realizar a substituição com controle de tolerância. O canal alpha dos pixels é preservado durante a troca.

**Funcionalidades:**

- Interface gráfica escura e moderna
- Seleção de imagem via explorador de arquivos
- Duas entradas HEX independentes (origem e destino) com prévia em tempo real
- Captura de cor clicando diretamente sobre a imagem (para ambas as cores)
- Seta visual mostrando a troca de cor em tempo real (`■ → ■`)
- Preview do pixel sob o cursor ao capturar cor (com contraste automático de texto)
- Controle de tolerância de 0 a 120
- Preview lado a lado (original × resultado) com fundo xadrez para transparência
- Processamento em thread separada (sem travar a UI)
- Exportação em PNG com alpha preservado

**Formatos de imagem suportados:** PNG, JPG, JPEG, BMP, WEBP, TIFF

## Pré-requisitos

- Python 3.10+
- Bibliotecas:

```bash
pip install Pillow numpy
```

> `tkinter` já vem incluído na instalação padrão do Python.

## Como usar

### 1. Execute o script

```bash
python color_replace.py
```

### 2. Selecione uma imagem

Clique em **📂 Procurar arquivo…** e escolha a imagem desejada. O preview original aparecerá à direita.

### 3. Defina a cor de origem

Digite o código HEX da cor que deseja substituir (ex: `FF0000` para vermelho) — ou clique em **Capturar da imagem** para clicar diretamente sobre a cor na imagem. Ao passar o mouse, uma prévia do pixel e seu código HEX aparecem em tempo real.

### 4. Defina a cor de destino

Da mesma forma, informe o HEX da cor que irá substituir a original (ex: `0000FF` para azul) — ou use o botão de captura.

A seta visual `■ → ■` entre os dois campos mostra a troca que será aplicada.

### 5. Ajuste a tolerância

Use o slider para controlar a sensibilidade da substituição:

| Valor | Comportamento |
|---|---|
| `0` | Substitui apenas pixels exatamente iguais à cor de origem |
| `30` | Padrão — substitui tons próximos |
| `120` | Substitui uma faixa ampla de cores similares |

### 6. Processe e salve

Clique em **▶ Trocar Cor**. Após o processamento, o resultado aparecerá no preview e o botão **💾 Salvar PNG** ficará ativo.

O arquivo é salvo com o nome `<original>_<ORIGEM>_para_<DESTINO>.png` na pasta `output/`.
