"""Camada semantica v9 (Gemini). Os prompts v9 estao embebidos e sao enviados
automaticamente a' API do Gemini com o video. Isto NAO toca nos modelos de detecao
(YOLO/bola) — e' uma camada separada por cima.

- PROMPT_TEMPO_UTIL (Batedor): video completo -> rallies (tempo util).
- PROMPT_FASES (Estratega): 1 rally -> fases taticas DEFESA/TRANSICAO/ATAQUE.
- PROMPT_PANCADAS (Tecnico): 1 rally -> pancadas e resultados.
"""
from __future__ import annotations
from typing import Optional
import json, re

PROMPT_TEMPO_UTIL = r"""És um analista de vídeo de padel. A câmara é FRONTAL. Analisa o vídeo COMPLETO do jogo em anexo e segmenta-o em rallies (pontos jogados).

REGRAS GLOBAIS
1. Timestamps no formato MM:SS.mmm (com milissegundos). Ancora cada tempo a um evento visível, nunca a uma estimativa.
2. Tolerância: para cada timestamp dá também "margem_ms" — a incerteza em milissegundos (ex.: 80 = ±80 ms). Se a incerteza for grande, aumenta a margem e baixa a confiança.
3. Vocabulário fechado: usa apenas os valores indicados. Se não conseguires classificar com segurança, usa "confianca": "baixa". NUNCA inventes um rally que não consigas ancorar a um serviço visível.
4. Identidade das equipas: identifica a Equipa A e a Equipa B pela cor da camisola.
5. Apresenta primeiro o raciocínio; só depois o JSON. O JSON tem de ser consistente com o raciocínio.

REGRAS DE DETEÇÃO DE RALLY
1. Início: todo o rally começa num SERVIÇO (1-2s antes do impacto do serviço).
2. Fim do ponto — CONFIRMAÇÃO AO CONTRÁRIO (regra principal): a última pancada de um rally só é confirmada como fim depois de ESPERAR 6 SEGUNDOS. Nesses 6s:
   - se aparecer outra pancada que NÃO seja serviço → o ponto NÃO tinha acabado; essa pancada pertence ao mesmo rally (recomeça a contar a partir dela).
   - se passarem os 6s sem qualquer pancada, OU se a pancada seguinte for um SERVIÇO → o ponto acabou na última pancada; o serviço seguinte inicia um NOVO rally.
   Os 6s são uma rede de segurança: cobrem o caso de uma pancada de um dos lados não ser detetada.
3. Atalhos de fim imediato: se vires claramente a bola SAIR DE CAMPO ou um jogador TOCAR NA REDE, o ponto acaba aí (não precisas de esperar os 6s).
4. A bola sair do ENQUADRAMENTO NÃO termina o rally (lob alto, bola ao fundo). "Inatividade" refere-se a PANCADAS e JOGADORES, nunca à bola estar fora do frame.
5. Inatividade de jogadores (confirmação rápida, opcional): se TODOS os jogadores estiverem visíveis e ficarem ~3s parados (sem deslocamento para jogar), podes confirmar o fim sem esperar os 6s. Se NÃO vires todos os jogadores na câmara, NÃO adivinhes — usa apenas a regra dos 6s.
6. Margem do clip (fecho): o fim do rally é no fim do ponto (última pancada confirmada pela regra 2; se não houver mais pancadas, corta aí). Ao cortar, acrescenta +2 SEGUNDOS depois desse ponto — apenas como margem visual para se ver bem o fim do clip (não é deteção).
7. Trocas de campo: se a pausa entre pontos for superior a 45s, reavalia as cores das camisolas e regista se a Equipa A mudou de lado.

ANTES DE EMITIR O JSON, verifica:
- total_rallies é igual ao número de entradas em "rallies".
- Em cada rally, fim > inicio e os rallies não se sobrepõem no tempo.
- Cada rally começa num SERVIÇO; cada fim foi confirmado por 6s sem outra pancada que não o serviço (ou por bola fora de campo / toque na rede).
- Não cortaste um rally só porque a bola saiu do enquadramento.
- Não declaraste inatividade sem teres todos os jogadores visíveis na câmara.
- Cada troca de campo está ancorada a uma pausa > 45s e tem as cores das camisolas reavaliadas.

OUTPUT (apenas este JSON após o raciocínio):
{
  "resumo": { "total_rallies": 0 },
  "trocas_de_campo": [
    { "timestamp": "00:00.000", "nova_posicao_equipa_A": "Lado Superior", "camisola_equipa_A": "[cor]", "camisola_equipa_B": "[cor]", "confianca": "alta" }
  ],
  "rallies": [
    { "id": 1, "inicio": "00:00.000", "fim": "00:00.000", "margem_ms": 80, "confianca": "alta" }
  ]
}"""

PROMPT_FASES = r"""És um analista tático de padel. A câmara é FRONTAL. O vídeo em anexo é UM ÚNICO RALLY. Fragmenta-o em micro-clips de confronto entre a Equipa A e a Equipa B.

REGRAS GLOBAIS
1. Timestamps no formato MM:SS.mmm. Ancora cada tempo a um evento visível.
2. Tolerância: dá "margem_ms" por timestamp (incerteza em ms; ex.: 80 = ±80 ms). Mais incerteza → maior margem e menor confiança.
3. Vocabulário de fases fechado: DEFESA, TRANSIÇÃO, ATAQUE. Na dúvida usa "confianca": "baixa". NUNCA inventes uma transição sem âncora visual.
4. Identifica a Equipa A e a Equipa B pela cor da camisola no início do clip.
5. Apresenta primeiro o raciocínio; só depois o JSON, consistente com o raciocínio.

COMO DEFINIR A FASE DE CADA EQUIPA (regra das duas boxes)
- A posição de cada jogador é a ARESTA INFERIOR da sua bounding box (ponto de contacto com o solo) — nunca a cabeça, o tronco ou o pé isolado.
- Duas marcas físicas no campo: a LINHA DE SERVIÇO (limite Defesa/Transição) e a INTERCEÇÃO MALHA 3 / MALHA 2 (limite Transição/Ataque). A faixa de transição (~4 m) fica entre as duas.
- Avalia as DUAS boxes de cada equipa em conjunto:
  • DEFESA = ambas as boxes atrás da linha de serviço.
  • ATAQUE = ambas as boxes à frente da interceção malha 3 / malha 2.
  • TRANSIÇÃO = tudo o resto (pelo menos uma box na faixa intermédia, ou as boxes em zonas diferentes — ex.: um jogador no fundo e outro na rede).
- TRANSIÇÃO é o estado-resíduo: só é DEFESA se forem AMBOS atrás da linha; só é ATAQUE se forem AMBOS à frente da junção.

COMO CORTAR OS CLIPS
1. Cada entrada é uma janela contínua onde A e B mantêm a mesma combinação de fases.
2. Abre uma NOVA entrada SEMPRE que QUALQUER das duas equipas muda de fase (uma box cruza uma marca e altera a fase da equipa). Conta-se por transições, não por combinações únicas — a mesma combinação pode repetir-se várias vezes no mesmo rally, e cada ocorrência é uma entrada independente.
3. Sem buracos nem sobreposições: o "fim" de uma entrada é igual ao "inicio" da seguinte. O "fim" da última entrada é o fim do rally.
4. Maximiza a granularidade: na dúvida entre fundir ou separar, SEPARA.
5. Cruzamento confirmado (anti-jitter): só conta como mudança de fase quando a aresta inferior da box passa CLARAMENTE a marca. Se a box apenas toca, treme ou oscila em cima da marca sem a atravessar de forma estável, NÃO abras nova entrada.
6. Análise frame a frame, apresentação por clip: INTERNAMENTE percorre o rally em resolução temporal fina (frame a frame), determinando a fase de cada equipa em cada instante, para localizares com precisão o momento exato de cada cruzamento de marca. NO OUTPUT, consolida instantes consecutivos com a mesma combinação A vs B num único clip (janela início→fim). Ou seja: raciocina ao frame, apresenta ao clip. A TRANSIÇÃO, por ser a fase mais dinâmica, beneficia especialmente desta análise fina — não percas nenhuma sub-janela de transição real.

EXEMPLO (dentro de um único rally):
Clip 1: Ataque (A) vs Defesa (B)     — estado inicial
Clip 2: Ataque (A) vs Transição (B)  — B cruza a linha de serviço (sobe)
Clip 3: Ataque (A) vs Ataque (B)     — B cruza a interceção malha 3/2 (sobe)
Clip 4: Ataque (A) vs Transição (B)  — B recua para a faixa intermédia
→ 4 clips, 3 transições. Os clips 2 e 4 têm o mesmo nome mas são entradas independentes.

RACIOCÍNIO (obrigatório, antes do JSON):
<raciocinio_tatico>
[Percorre o rally em resolução fina, frame a frame, acompanhando a fase das duas equipas; só depois consolidas em clips para o JSON.]
Estado inicial [MM:SS.mmm]: Equipa A = [fase] (boxes em [zona]); Equipa B = [fase] (boxes em [zona]). → Entrada 1.
Aos [MM:SS.mmm]: Equipa [A/B] — box [Xn] cruza [Linha de Serviço / Interceção malha 3-2]; a fase da equipa passa de [fase] para [fase]. → Nova entrada.
[Repetir para CADA mudança de fase de qualquer equipa.]
Fim do rally [MM:SS.mmm].
</raciocinio_tatico>

ANTES DE EMITIR O JSON, verifica:
- Número de entradas = número de transições + 1.
- Para cada entrada i: fim[i] == inicio[i+1] (sem buracos nem sobreposições).
- inicio da 1ª entrada == início do rally; fim da última == fim do rally.
- Cada transição tem âncora visual (que box cruzou que marca).

OUTPUT (apenas este JSON após o raciocínio):
{
  "rally_id": 1,
  "total_transicoes": 0,
  "confrontos_taticos": [
    {
      "clip": 1,
      "fase_equipa_A": "ATAQUE",
      "fase_equipa_B": "DEFESA",
      "fase_confronto": "Equipa A ATAQUE vs Equipa B DEFESA",
      "inicio": "00:00.000",
      "fim": "00:00.000",
      "margem_ms": 80,
      "gatilho": "estado inicial",
      "confianca": "alta"
    }
  ]
}"""

PROMPT_PANCADAS = r"""És um analista técnico de padel. A câmara é FRONTAL. O vídeo em anexo é UM ÚNICO RALLY. Identifica as pancadas e os resultados de UMA SÓ EQUIPA — a equipa-alvo (indica abaixo qual: A ou B).

EQUIPA-ALVO: [A]

REGRAS GLOBAIS
1. Timestamps no formato MM:SS.mmm. Ancora cada tempo a um evento visível.
2. Tolerância: dá "margem_ms" por timestamp (incerteza em ms; ex.: 80 = ±80 ms).
3. Vocabulário fechado (ver listas abaixo). Se não conseguires classificar, usa "indeterminado" e "confianca": "baixa". NUNCA inventes uma pancada sem âncora visual.
4. Identifica os jogadores da equipa-alvo pela cor da camisola e posição inicial.
5. Apresenta primeiro o raciocínio; só depois o JSON, consistente com o raciocínio.

TAXONOMIA (dois eixos independentes — preenche sempre os dois):
- "tipo" (como se bate): serve, volley, forehand, backhand, overhead, bandeja, vibora, indeterminado.
- "contexto" (situação da bola): normal, saida_parede_fundo, saida_parede_lateral, contra_parede, indeterminado.

RESULTADO (ancorado ao fim do rally) — só a ÚLTIMA pancada do rally pode ser winner ou erro; as restantes são "neutro" por defeito:
- winner = bola que o adversário não toca e que termina o ponto a favor do alvo.
- erro_nao_forcado = falha do alvo sem pressão (bola fácil, sem deslocamento exigente).
- erro_forcado = falha do alvo sob pressão clara do adversário.
- neutro = mantém a bola em jogo sem vantagem nem erro visível.

RACIOCÍNIO (obrigatório, antes do JSON):
<raciocinio_tecnico>
1. Preparação: "Aos [MM:SS.mmm], [Jogador] arma [tipo] em contexto [contexto]."
2. Execução: "Aos [MM:SS.mmm], [Jogador] conclui."
3. Resultado: "Resultado: [winner / erro_forcado / erro_nao_forcado / neutro]."
[Repetir por pancada.]
</raciocinio_tecnico>

ANTES DE EMITIR O JSON, verifica:
- Só a última pancada tem resultado diferente de "neutro" (exceto se houver erro do alvo a meio do rally).
- Coerência ponto/pancada: se equipa_ganha_ponto == alvo, a última pancada do alvo é winner ou houve erro do adversário; se for diferente do alvo, a última ação do alvo é um erro.

OUTPUT (apenas este JSON após o raciocínio):
{
  "rally_id": 1,
  "equipa_alvo": "A",
  "jogadores": [
    { "id": "A1", "desc": "camisola [cor], posição inicial [zona]" },
    { "id": "A2", "desc": "camisola [cor], posição inicial [zona]" }
  ],
  "pancadas": [
    {
      "timestamp": "00:00.000",
      "margem_ms": 80,
      "jogador": "A1",
      "tipo": "serve",
      "contexto": "normal",
      "resultado": "neutro",
      "confianca": "alta"
    }
  ],
  "servico_valido": true,
  "equipa_ganha_ponto": "A"
}"""

PROMPTS = {"tempo_util": PROMPT_TEMPO_UTIL, "fases": PROMPT_FASES, "pancadas": PROMPT_PANCADAS}


def analyze_video(
    video_path: str,
    which: str = "tempo_util",
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash",
    mock: bool = False,
) -> dict:
    """Corre um prompt v9 sobre um video via Gemini. Devolve {text, json}.

    which: "tempo_util" | "fases" | "pancadas".
    mock=True (ou sem api_key): nao chama a rede; devolve so o prompt usado (para testes).
    """
    if which not in PROMPTS:
        raise ValueError(f"which deve ser um de {list(PROMPTS)}")
    prompt = PROMPTS[which]
    if mock or not api_key:
        return {"mock": True, "which": which, "prompt_chars": len(prompt)}

    import google.generativeai as genai  # import tardio (opcional)
    import time
    genai.configure(api_key=api_key)
    f = genai.upload_file(video_path)
    while f.state.name == "PROCESSING":
        time.sleep(3); f = genai.get_file(f.name)
    resp = genai.GenerativeModel(model).generate_content([prompt, f])
    text = resp.text
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0)) if m else None
    return {"text": text, "json": data, "which": which}
