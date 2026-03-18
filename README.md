# 🏆 Cartola Specialist Analyzer

Template de análise pré-escalação para Cartola FC baseado em **metodologia de especialista**. Um framework estruturado que força você a **analisar antes de escalar**.

## 📋 O que é?

Um **checklist de 6 etapas** que você executa antes de qualquer escalação no Cartola:

1. **Leitura de Rodada** - Identifique favoritos, jogos abertos e pegados
2. **Patrimônio** - Defina postura (mitar, valorizar, meio-termo) e MPV
3. **Scouts** - Filtre por média, padrão e consistência
4. **Contexto** - Confrontos, desfalques, sequência e força dos times
5. **Gestão de Risco** - Fuga de manada, controle de exposição
6. **Capitão** - Escolha por teto de pontos e confronto favorável

## 🚀 Estrutura do Repositório

```
cartola-specialist-analyzer/
├── analyzer/                    # Núcleo do analisador
│   ├── __init__.py
│   ├── models.py               # Modelos de dados (Pydantic)
│   ├── checklist.py            # ⭐ Template do checklist (CORE)
│   ├── analyzer.py             # Orquestrador principal
│   └── scouts.py               # Cálculos de scouts
├── examples/
│   └── rodada_38_2025.py       # Exemplo completo de uso
├── templates/
│   ├── pre_escalacao.json      # Template JSON para preencher
│   └── exemplo_rodada.json     # Exemplo preenchido
├── scripts/
│   ├── analyze.py              # CLI (roadmap)
│   └── generate_report.py      # Relatório em Markdown (roadmap)
├── requirements.txt
├── README.md
└── LICENSE
```

## 💻 Como Usar

### 1. **Instalação Rápida**

```bash
git clone https://github.com/RickTheBoy-ops/cartola-specialist-analyzer.git
cd cartola-specialist-analyzer
pip install -r requirements.txt
```

### 2. **Uso via Python (Recomendado)**

```python
from analyzer import SpecialistAnalyzer, Match, Team, Player, PostureEnum

# 1. Cria analisador
analyzer = SpecialistAnalyzer(rodada=38, budget=100.0)

# 2. Carrega dados (partidas, times, jogadores)
# ... (preencha com dados reais do Cartola)

# 3. Executa análise
response = analyzer.analyze(
    matches=matches,
    posture=PostureEnum.MEIO_TERMO  # ou MITAR / VALORIZAR
)

# 4. Obtém relatório
print(analyzer.get_report())

# 5. Acessa resposta estruturada
print(f"Capitão recomendado: {response.recommended_captain.name}")
print(f"Confiança: {response.confidence_level:.1f}%")
```

### 3. **Executar Exemplo**

```bash
python examples/rodada_38_2025.py
```

## 🎯 Metodologia: As 6 Etapas

### Etapa 1: Leitura de Rodada
Analisa a rodada em alto nível:
- Quais times são favoritos?
- Quais jogos tendem a gols?
- Quais jogos são pegados/truncados?

### Etapa 2: Patrimônio
Define estratégia e calcula MPV:
- **Mitar**: 30-40% em baratos, apostas agressivas
- **Valorizar**: 70-80% em seguros com alto teto
- **Meio-termo**: 60% segurança, 40% oportunidade

### Etapa 3: Scouts
Filtra jogadores por:
- Média de pontos >= 5
- Consistência >= 70%
- Padrão de scouts

### Etapa 4: Contexto
Avalia:
- Força de cada confronto
- Desfalques e suspensões
- Sequência recente

### Etapa 5: Gestão de Risco
Implementa regras:
- Max 2 defensores do mesmo time
- Max 3 jogadores totais do mesmo time
- 1-2 apostas diferenciais

### Etapa 6: Capitão
Escolhe por:
- Maior teto de pontos
- Confronto favorável
- Consistência alta

## 🤝 Contribuir

Sugestões e melhorias são bem-vindas!

## 📄 Licença

MIT License

---

**Desenvolvido para especialistas em Cartola FC**
