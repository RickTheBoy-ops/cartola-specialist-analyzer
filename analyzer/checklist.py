"""Template de checklist pré-escalação para Cartola FC.

Este módulo força 6 etapas de análise antes de qualquer escalação:

1. LEITURA DE RODADA: Identifiquer favoritos, jogos abertos/pegados
2. PATRIMÔNIO: Postura (mitar/valorizar/meio-termo) e MÍNIMO PARA VALORIZAR
3. SCOUTS: Filtrar por média, padrão de scouts, consistência
4. CONTEXTO: Confrontos, sequência, desfalques, força dos times
5. GESTÃO DE RISCO: Escape de manada, controle de exposição
6. CAPITÃO: Escolha por teto de pontos e confronÃo mais favorável

MPV (Mínimo Para Valorizar):
- Fórmula CORRETA: quantos pontos o jogador precisa fazer para valorizar de preço
- Se custa R$7 e média é 7 pts, precisa de ~7.5-8 pts para subir de preço
- Quanto MENOR o MPV, mais fácil valorizar (jogador barato com potencial)
"""

from datetime import datetime
from typing import List, Optional, Dict, Tuple
from .models import (
    Match,
    Player,
    Team,
    ChecklistResponse,
    AnalysisStep,
    PostureEnum,
    RiskProfile,
)


class CartolaPrescalingChecklist:
    """Checklist de especialista para pré-escalação."""

    def __init__(self, rodada: int, budget: float, posture: PostureEnum = PostureEnum.MEIO_TERMO):
        self.rodada = rodada
        self.budget = budget
        self.posture = posture
        self.matches: List[Match] = []
        self.all_players: List[Player] = []
        self.response: Optional[ChecklistResponse] = None

    def load_matches(self, matches: List[Match]):
        """Carrega as partidas da rodada."""
        self.matches = matches
        # Extrai todos os jogadores de todos os times
        self.all_players = []
        for match in self.matches:
            self.all_players.extend(match.home_team.players)
            self.all_players.extend(match.away_team.players)

    # ============================================================
    # STEP 1: LEITURA DE RODADA
    # ============================================================
    def step1_leitura_rodada(self) -> AnalysisStep:
        """Etapa 1: Análise geral da rodada.
        
        Identifica:
        - Quais times são favoritos
        - Quais jogos tendem a mais gols
        - Quais jogos são pegados/truncados
        """
        findings = []
        recommendations = []

        # Ordena partidas por probabilidade de gols
        matches_by_goals = sorted(
            self.matches,
            key=lambda m: m.expected_goals,
            reverse=True
        )

        if matches_by_goals:
            top_goals = matches_by_goals[:2]
            findings.append(f"Jogos com maior tendência a gols: {', '.join([f'{m.home_team.name} vs {m.away_team.name}' for m in top_goals])}")
            recommendations.append(f"Priorize atacantes e meias dos times: {', '.join(set([m.home_team.name for m in top_goals] + [m.away_team.name for m in top_goals]))}")

        # Identifica favoritos
        favorites = [
            m for m in self.matches
            if m.probability_home_win > 0.45 or m.probability_away_win > 0.45
        ]
        if favorites:
            findings.append(f"Partidas com favorito claro: {len(favorites)}/{len(self.matches)}")
            for m in favorites:
                favorite = m.home_team.name if m.probability_home_win > m.probability_away_win else m.away_team.name
                findings.append(f"  - {favorite} é favorito")

        return AnalysisStep(
            step_number=1,
            step_name="Leitura de Rodada",
            completed=True,
            findings=findings,
            recommendations=recommendations,
            confidence=0.9
        )

    # ============================================================
    # STEP 2: PATRIMÔNIO
    # ============================================================
    def step2_patrimonio(self) -> AnalysisStep:
        """Etapa 2: Análise de patrimônio e MPV.
        
        Calcula:
        - Postura (mitar, valorizar, meio-termo)
        - Mínimo Para Valorizar (MPV) por jogador
        - Oportunidades de valorização
        
        MPV CORRIGIDO:
        - Preço atual: R$7.00
        - Média: 7 pts
        - MPV = pontos necessários para subir de preço (~0.5% do preço base)
        - Logo: MPV ≈ 7.5-8 pts (pouco acima da média)
        """
        findings = []
        recommendations = []

        findings.append(f"Orçamento total: R${self.budget:.1f}M")
        findings.append(f"Postura: {self.posture.value.upper()}")

        # Define estratégia por postura
        if self.posture == PostureEnum.MITAR:
            findings.append("Estratégia: AGRESSIVA - Foco em jogadores baratos com alto potencial")
            recommendations.append("Escale 30-40% do orçamento em jogadores abaixo da média de preço")
            recommendations.append("Use 1-2 apostas diferenciais em ataque")
        elif self.postura == PostureEnum.VALORIZAR:
            findings.append("Estratégia: CONSERVADORA - Foco em jogadores seguros com chance de subir preço")
            recommendations.append("Escale 70-80% do orçamento em jogadores com preço abaixo da média + alto teto")
            recommendations.append("Evite apostas muito arriscadas")
        else:  # MEIO_TERMO
            findings.append("Estratégia: BALANÇADA - 50% segurança, 50% oportunidade")
            recommendations.append("Escale 60% em jogadores seguros, 40% em oportunidades")

        # Calcula MPV CORRIGIDO para cada jogador
        # MPV = mínimo de pontos para o jogador valorizar (subir de preço)
        # Cartola: valoriza ~0.5-1 ponto acima da média
        mpv_analysis = []
        for player in self.all_players:
            if player.average_points > 0:
                # MPV é a média + um incremento pequeno (0.5 a 1 ponto)
                # Quanto MENOR este valor, mais fácil de valorizar
                mpv = player.average_points + 0.5  # Precisa fazer ~0.5 pts acima da média
                player.mpv = mpv
                if player.price < 5.0:  # Jogador barato
                    mpv_analysis.append((player.name, player.price, player.average_points, mpv))

        if mpv_analysis:
            mpv_analysis.sort(key=lambda x: x[3])  # Ordena por MPV (menor = mais fácil valorizar)
            findings.append(f"Top 3 baratos com melhor MPV (mais fácil valorizar):")
            for name, price, avg, mpv in mpv_analysis[:3]:
                findings.append(f"  - {name} (R${price:.1f}M, Média: {avg:.1f} pts, Precisa: {mpv:.1f} pts)")

        return AnalysisStep(
            step_number=2,
            step_name="Patrimônio",
            completed=True,
            findings=findings,
            recommendations=recommendations,
            confidence=0.85
        )

    # ============================================================
    # STEP 3: SCOUTS
    # ============================================================
    def step3_scouts(self) -> AnalysisStep:
        """Etapa 3: Análise de scouts e médias.
        
        Filtra jogadores por:
        - Média de pontos
        - Consistência (% de rodadas jogadas)
        - Padrão de scouts (quem gera scouts positivos)
        """
        findings = []
        recommendations = []

        # Filtra jogadores com boa média
        good_avg = [
            p for p in self.all_players
            if p.average_points >= 5.0 and p.status == "Disponível"
        ]
        good_avg.sort(key=lambda x: x.average_points, reverse=True)

        findings.append(f"Jogadores com média >= 5 pontos: {len(good_avg)}")
        if good_avg:
            findings.append("Top 5 médias absolutas:")
            for i, player in enumerate(good_avg[:5], 1):
                findings.append(f"  {i}. {player.name} ({player.position} - {player.team}): {player.average_points:.1f} pts")
                recommendations.append(f"Priorize {player.name} se tiver condição tática")

        # Filtra por consistência
        consistent = [
            p for p in self.all_players
            if p.consistency >= 70 and p.status == "Disponível"
        ]
        findings.append(f"Jogadores com 70%+ de consistência: {len(consistent)}")

        # Analisa padrão de scouts
        findings.append("\nJogadores com melhor padrão de scouts (média + consistência):")
        scout_score = [
            (p, p.average_points * (p.consistency / 100))
            for p in good_avg[:10]
        ]
        scout_score.sort(key=lambda x: x[1], reverse=True)
        for player, score in scout_score[:3]:
            findings.append(f"  - {player.name}: {score:.2f} (média {player.average_points:.1f}, consist. {player.consistency:.0f}%)")

        return AnalysisStep(
            step_number=3,
            step_name="Scouts",
            completed=True,
            findings=findings,
            recommendations=recommendations,
            confidence=0.88
        )

    # ============================================================
    # STEP 4: CONTEXTO
    # ============================================================
    def step4_contexto(self) -> AnalysisStep:
        """Etapa 4: Análise de contexto e confrontos.
        
        Avalia:
        - Força dos adversários
        - Desfalques e suspensões
        - Sequência recente
        - Mudanças de posição tática
        """
        findings = []
        recommendations = []

        findings.append("Análise de confrontos:")
        for match in self.matches:
            if match.home_team.strength > match.away_team.strength:
                diff = match.home_team.strength - match.away_team.strength
                findings.append(f"  {match.home_team.name} (casa) vs {match.away_team.name}: Vantagem {diff:.1%}")
                recommendations.append(f"Priorize atacantes de {match.home_team.name}")
            else:
                diff = match.away_team.strength - match.home_team.strength
                findings.append(f"  {match.home_team.name} vs {match.away_team.name} (visita): Vantagem visitante {diff:.1%}")

        # Desfalques
        injured = [p for p in self.all_players if "les" in p.status.lower()]
        if injured:
            findings.append(f"\nAtenvolvão: {len(injured)} jogadores lesionados")
            recommendations.append(f"Evite escalas de lesionados ou volta de lesão")

        # Forma recente
        findings.append("\nForma recente dos times:")
        for match in self.matches:
            findings.append(f"  {match.home_team.name}: {match.home_team.recent_form:.0%}")
            findings.append(f"  {match.away_team.name}: {match.away_team.recent_form:.0%}")

        return AnalysisStep(
            step_number=4,
            step_name="Contexto",
            completed=True,
            findings=findings,
            recommendations=recommendations,
            confidence=0.82
        )

    # ============================================================
    # STEP 5: GESTÃO DE RISCO
    # ============================================================
    def step5_gestao_risco(self) -> AnalysisStep:
        """Etapa 5: Gestão de risco e fuga de manada.
        
        Implementa:
        - Evita concentração de risco (max 2 defensores do mesmo time)
        - Busca 1-2 apostas diferenciais
        - Controla exposição em times frágeis
        """
        findings = []
        recommendations = []

        findings.append("Diretrizes de risco:")
        recommendations.append("Máximo 2 defensores do mesmo time (evita risco de SG)")
        recommendations.append("Máximo 3 jogadores do mesmo time (qualquer posição)")
        recommendations.append("Pelo menos 1 aposta diferencial em ataque (jogador menos escalado)")
        recommendations.append("Capitão com 70%+ chance de cumprir média")

        # Calcula "escalabilidade" de cada jogador
        low_risk = [
            p for p in self.all_players
            if p.average_points >= 6.0
            and p.consistency >= 80
            and p.status == "Disponível"
            and p.risk_profile == RiskProfile.ALTO
        ]

        medium_risk = [
            p for p in self.all_players
            if p.risk_profile == RiskProfile.MODERADO and p.status != "Lesionado"
        ]

        findings.append(f"\nJogadores baixo risco (seguros): {len(low_risk)}")
        findings.append(f"Jogadores risco moderado (apostas): {len(medium_risk)}")

        # Distribuição por time
        teams_exposure = {}
        for player in self.all_players:
            if player.team not in teams_exposure:
                teams_exposure[player.team] = 0
            teams_exposure[player.team] += 1

        findings.append(f"\nDistribuição de jogadores por time:")
        for team, count in sorted(teams_exposure.items(), key=lambda x: x[1], reverse=True)[:5]:
            findings.append(f"  - {team}: {count} disponíveis")

        return AnalysisStep(
            step_number=5,
            step_name="Gestão de Risco",
            completed=True,
            findings=findings,
            recommendations=recommendations,
            confidence=0.80
        )

    # ============================================================
    # STEP 6: CAPITÃO
    # ============================================================
    def step6_capitao(self) -> Tuple[AnalysisStep, Optional[Player]]:
        """Etapa 6: Escolha do capitão.
        
        Critérios:
        - Jogador com maior teto de pontos
        - Confronto mais favorável
        - Confiança na média
        """
        findings = []
        recommendations = []
        captain = None

        # Calcula ceiling (teto) de cada jogador
        players_with_ceiling = []
        for player in self.all_players:
            if player.status == "Disponível":
                ceiling = player.average_points * 1.5  # Teto otimista
                players_with_ceiling.append((player, ceiling))

        # Ordena por ceiling e filtra por média alta
        players_with_ceiling.sort(key=lambda x: x[1], reverse=True)
        top_ceilings = [
            (p, c) for p, c in players_with_ceiling
            if p.average_points >= 6.0
        ][:5]

        if top_ceilings:
            findings.append("Top 5 capitães candidatos (por teto de pontos):")
            for i, (player, ceiling) in enumerate(top_ceilings, 1):
                findings.append(f"  {i}. {player.name} (Média: {player.average_points:.1f}, Teto: {ceiling:.1f})")
                recommendations.append(f"{player.name} vs confronto favorável = oportunidade de {ceiling:.0f} pontos")

            # Escolhe o primeiro (maior teto + melhor confiança)
            captain = top_ceilings[0][0]
            findings.append(f"\n🏆 CAPITÃO RECOMENDADO: {captain.name}")
            findings.append(f"   Razão: Maior teto ({top_ceilings[0][1]:.1f}), média alta ({captain.average_points:.1f})")
        else:
            findings.append("Nenhum jogador com perfil ideal de capitão (média < 6)")

        return (
            AnalysisStep(
                step_number=6,
                step_name="Capitão",
                completed=True,
                findings=findings,
                recommendations=recommendations,
                confidence=0.75
            ),
            captain
        )

    # ============================================================
    # EXECUTA O CHECKLIST COMPLETO
    # ============================================================
    def run(self) -> ChecklistResponse:
        """Executa todas as 6 etapas do checklist."""
        step1 = self.step1_leitura_rodada()
        step2 = self.step2_patrimonio()
        step3 = self.step3_scouts()
        step4 = self.step4_contexto()
        step5 = self.step5_gestao_risco()
        step6, captain = self.step6_capitao()

        # Calcula confiança geral
        avg_confidence = (
            step1.confidence + step2.confidence + step3.confidence +
            step4.confidence + step5.confidence + step6.confidence
        ) / 6 * 100

        # Calcula risco geral
        risk_score = 1 - avg_confidence / 100

        self.response = ChecklistResponse(
            rodada=self.rodada,
            timestamp=datetime.now(),
            budget=self.budget,
            postura=self.postura,
            step1_leitura_rodada=step1,
            step2_patrimonio=step2,
            step3_scouts=step3,
            step4_contexto=step4,
            step5_gestao_risco=step5,
            step6_capitao=step6,
            recommended_captain=captain,
            confidence_level=avg_confidence,
            risk_score=risk_score,
        )

        return self.response

    def get_report(self) -> str:
        """Gera relatório markdown do checklist."""
        if not self.response:
            return "Checklist não foi executado. Execute .run() primeiro."

        report = f"""# 🏆 Cartola - Análise Pré-Escalação

**Rodada:** {self.response.rodada}  
**Data:** {self.response.timestamp.strftime('%d/%m/%Y %H:%M')}  
**Orçamento:** R$ {self.response.budget:.1f}M  
**Postura:** {self.response.postura.value.upper()}  
**Confiança Geral:** {self.response.confidence_level:.1f}%  
**Risco:** {self.response.risk_score:.1%}  

---
"""

        # Formata cada etapa
        for step in [
            self.response.step1_leitura_rodada,
            self.response.step2_patrimonio,
            self.response.step3_scouts,
            self.response.step4_contexto,
            self.response.step5_gestao_risco,
            self.response.step6_capitao,
        ]:
            report += f"\n## {step.step_number}. {step.step_name.upper()}\n\n"
            
            if step.findings:
                report += "**Achados:**\n"
                for finding in step.findings:
                    report += f"- {finding}\n"
                report += "\n"
            
            if step.recommendations:
                report += "**Recomendações:**\n"
                for rec in step.recommendations:
                    report += f"- {rec}\n"
                report += "\n"

            report += f"**Confiança:** {step.confidence:.0%}\n\n"

        # Capitão recomendado
        if self.response.recommended_captain:
            report += f"\n## 🏆 CAPITÃO RECOMENDADO\n\n"
            cap = self.response.recommended_captain
            report += f"**{cap.name}** ({cap.position} - {cap.team})  \n"
            report += f"Média: {cap.average_points:.1f} pts | Preço: R${cap.price:.1f}M | Consist.: {cap.consistency:.0f}%\n"

        report += "\n---\n*Gerado automaticamente por Cartola Specialist Analyzer*"

        return report
