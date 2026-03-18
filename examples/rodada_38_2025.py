#!/usr/bin/env python3
"""Exemplo de uso: Análise completa da Rodada 38 (2025).

Demonstra como usar o CartolaPrescalingChecklist para analisar
qualquer rodada do Cartola FC seguindo a metodologia de especialista.

Usage:
    python examples/rodada_38_2025.py
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from analyzer import (
    SpecialistAnalyzer,
    CartolaPrescalingChecklist,
    Match,
    Team,
    Player,
    PostureEnum,
    RiskProfile,
)


def create_example_players() -> list:
    """Cria jogadores de exemplo com dados realistas."""
    players = []
    
    # Botafogo
    players.extend([
        Player(
            player_id=1,
            name="Amir",
            position="GOL",
            team="Botafogo",
            price=3.5,
            average_points=6.2,
            scouts=[],
            consistency=95,
            matches_played=37,
            minutes_played=3330,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=2,
            name="Victor Cogo",
            position="ZG",
            team="Botafogo",
            price=5.0,
            average_points=5.5,
            scouts=[],
            consistency=88,
            matches_played=33,
            minutes_played=2970,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=3,
            name="Luiz Araújo",
            position="Ata",
            team="Botafogo",
            price=8.0,
            average_points=7.8,
            scouts=[],
            consistency=92,
            matches_played=35,
            minutes_played=2890,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=4,
            name="Savarino",
            position="Ata",
            team="Botafogo",
            price=9.5,
            average_points=8.1,
            scouts=[],
            consistency=85,
            matches_played=32,
            minutes_played=2200,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
    ])
    
    # Palmeiras
    players.extend([
        Player(
            player_id=10,
            name="Weverton",
            position="GOL",
            team="Palmeiras",
            price=3.2,
            average_points=6.8,
            scouts=[],
            consistency=97,
            matches_played=37,
            minutes_played=3330,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=11,
            name="Estevão",
            position="Ata",
            team="Palmeiras",
            price=11.0,
            average_points=8.5,
            scouts=[],
            consistency=87,
            matches_played=33,
            minutes_played=2500,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=12,
            name="Rony",
            position="Ata",
            team="Palmeiras",
            price=7.5,
            average_points=6.9,
            scouts=[],
            consistency=80,
            matches_played=30,
            minutes_played=1800,
            status="Disponível",
            risk_profile=RiskProfile.MODERADO,
        ),
    ])
    
    # Flamengo
    players.extend([
        Player(
            player_id=20,
            name="Rossi",
            position="GOL",
            team="Flamengo",
            price=3.8,
            average_points=6.1,
            scouts=[],
            consistency=91,
            matches_played=34,
            minutes_played=3060,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=21,
            name="Bruno Henrique",
            position="Ata",
            team="Flamengo",
            price=9.0,
            average_points=7.4,
            scouts=[],
            consistency=88,
            matches_played=33,
            minutes_played=2400,
            status="Disponível",
            risk_profile=RiskProfile.MODERADO,
        ),
        Player(
            player_id=22,
            name="Gerson",
            position="Vol",
            team="Flamengo",
            price=8.5,
            average_points=6.8,
            scouts=[],
            consistency=83,
            matches_played=31,
            minutes_played=2200,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
    ])
    
    # São Paulo
    players.extend([
        Player(
            player_id=30,
            name="Rafael",
            position="GOL",
            team="São Paulo",
            price=3.0,
            average_points=5.8,
            scouts=[],
            consistency=89,
            matches_played=33,
            minutes_played=2970,
            status="Disponível",
            risk_profile=RiskProfile.ALTO,
        ),
        Player(
            player_id=31,
            name="Calleri",
            position="Ata",
            team="São Paulo",
            price=7.0,
            average_points=5.2,
            scouts=[],
            consistency=75,
            matches_played=28,
            minutes_played=1800,
            status="Provvel",  # RISCO
            risk_profile=RiskProfile.MODERADO,
        ),
    ])
    
    return players


def create_example_matches() -> list:
    """Cria partidas de exemplo para a rodada."""
    
    # Times
    botafogo_players = [p for p in create_example_players() if p.team == "Botafogo"]
    botafogo = Team(
        team_id=1,
        name="Botafogo",
        players=botafogo_players,
        strength=0.8,
        home=True,
        recent_form=0.85,
    )
    
    palmeiras_players = [p for p in create_example_players() if p.team == "Palmeiras"]
    palmeiras = Team(
        team_id=2,
        name="Palmeiras",
        players=palmeiras_players,
        strength=0.75,
        home=False,
        recent_form=0.80,
    )
    
    flamengo_players = [p for p in create_example_players() if p.team == "Flamengo"]
    flamengo = Team(
        team_id=3,
        name="Flamengo",
        players=flamengo_players,
        strength=0.78,
        home=True,
        recent_form=0.75,
    )
    
    sao_paulo_players = [p for p in create_example_players() if p.team == "São Paulo"]
    sao_paulo = Team(
        team_id=4,
        name="São Paulo",
        players=sao_paulo_players,
        strength=0.70,
        home=False,
        recent_form=0.65,
    )
    
    # Partidas
    matches = [
        Match(
            match_id=1,
            rodada=38,
            home_team=botafogo,
            away_team=palmeiras,
            probability_home_win=0.42,
            probability_draw=0.30,
            probability_away_win=0.28,
            over_25_goals=0.65,
            expected_goals=2.8,
            kick_off=datetime(2025, 12, 8, 16, 0),
        ),
        Match(
            match_id=2,
            rodada=38,
            home_team=flamengo,
            away_team=sao_paulo,
            probability_home_win=0.48,
            probability_draw=0.28,
            probability_away_win=0.24,
            over_25_goals=0.55,
            expected_goals=2.3,
            kick_off=datetime(2025, 12, 8, 18, 30),
        ),
    ]
    
    return matches


def main():
    """Executa análise de exemplo."""
    print("\n" + "=" * 60)
    print("🏆 CARTOLA SPECIALIST ANALYZER - EXEMPLO DE USO")
    print("=" * 60 + "\n")
    
    # Cria analisador
    analyzer = SpecialistAnalyzer(rodada=38, budget=100.0)
    
    # Carrega partidas de exemplo
    matches = create_example_matches()
    
    print(f"\u2705 Partidas carregadas: {len(matches)}")
    for match in matches:
        print(f"   - {match.home_team.name} vs {match.away_team.name}")
    
    # Executa análise
    print(f"\n⏳ Executando análise com postura: MEIO-TERMO...\n")
    response = analyzer.analyze(
        matches=matches,
        posture=PostureEnum.MEIO_TERMO,
    )
    
    # Exibe relatório
    print(analyzer.get_report())
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"Confiança Geral: {response.confidence_level:.1f}%")
    print(f"Score de Risco: {response.risk_score:.1%}")
    if response.recommended_captain:
        print(f"🏆 Capitão: {response.recommended_captain.name}")
    print("\n")


if __name__ == "__main__":
    main()
