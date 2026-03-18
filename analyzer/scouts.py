"""Cálculos de scouts para Cartola FC.

Pontos por scout:
- Gol (atacante): +8 pts
- Gol (outros): +5 pts
- Assistência: +5 pts
- SG (Sem-Gol): +5 pts
- Defesa: +1.3 pts
- Desarme: +1.5 pts
- Cartão amarelo: -1 pt
- Cartão vermelho: -3 pts
- Gol sofrido (def/volante): -2 pts
- Gol sofrido (meia): -1 pt
- Gol sofrido (atacante): 0 pts
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ScoutPointSystem:
    """Sistema de pontos de scouts do Cartola FC."""
    
    # Gols
    GOAL_ATTACKER = 8.0
    GOAL_OTHER = 5.0
    
    # Assists e SG
    ASSIST = 5.0
    SEM_GOL = 5.0  # Clean sheet (SG)
    
    # Defesa
    TACKLE = 1.5  # Desarme
    DEFENSE = 1.3  # Defesa
    
    # Negativos
    YELLOW_CARD = -1.0
    RED_CARD = -3.0
    
    # Gol sofrido
    GOAL_CONCEDED_DEFENDER = -2.0
    GOAL_CONCEDED_MIDFIELDER = -1.0
    GOAL_CONCEDED_ATTACKER = 0.0


class ScoutCalculator:
    """Calcula pontos baseado em scouts."""
    
    points_system = ScoutPointSystem()
    
    @staticmethod
    def calculate_player_points(
        position: str,
        goals: int = 0,
        assists: int = 0,
        sem_gol: bool = False,
        tackles: int = 0,
        defenses: int = 0,
        yellow_cards: int = 0,
        red_cards: int = 0,
        goals_conceded: int = 0,
    ) -> float:
        """Calcula pontos totais de um jogador baseado em seus scouts.
        
        Args:
            position: Posição do jogador (GOL, ZG, LD, LE, ZC, Vol, Mei, Ata)
            goals: Número de gols marcados
            assists: Número de assistências
            sem_gol: Se teve SG (clean sheet)
            tackles: Número de desarmes
            defenses: Número de defesas
            yellow_cards: Número de cartões amarelos
            red_cards: Número de cartões vermelhos
            goals_conceded: Número de gols sofridos (para defensores/goleiros)
            
        Returns:
            Pontos totais da rodada
        """
        points = 0.0
        
        # Gols
        if position in ["Ata"]:
            points += goals * ScoutCalculator.points_system.GOAL_ATTACKER
        else:
            points += goals * ScoutCalculator.points_system.GOAL_OTHER
        
        # Assistências
        points += assists * ScoutCalculator.points_system.ASSIST
        
        # SG
        if sem_gol and goals_conceded == 0:
            points += ScoutCalculator.points_system.SEM_GOL
        
        # Defesa
        points += tackles * ScoutCalculator.points_system.TACKLE
        points += defenses * ScoutCalculator.points_system.DEFENSE
        
        # Cartões
        points += yellow_cards * ScoutCalculator.points_system.YELLOW_CARD
        points += red_cards * ScoutCalculator.points_system.RED_CARD
        
        # Gol sofrido
        if position in ["GOL", "ZG", "LD", "LE", "ZC"]:
            if position == "GOL":
                points += goals_conceded * ScoutCalculator.points_system.GOAL_CONCEDED_DEFENDER
            elif position in ["ZG", "LD", "LE", "ZC"]:
                points += goals_conceded * ScoutCalculator.points_system.GOAL_CONCEDED_DEFENDER
            elif position == "Vol":
                points += goals_conceded * ScoutCalculator.points_system.GOAL_CONCEDED_MIDFIELDER
        
        return max(0.0, points)  # Ninguém pode ter pontos negativos (mínimo 0)
    
    @staticmethod
    def get_scout_breakdown(points: float) -> Dict[str, float]:
        """Decompõe os pontos em scouts individuais para análise."""
        return {
            "gol_atacante": ScoutCalculator.points_system.GOAL_ATTACKER,
            "gol_outro": ScoutCalculator.points_system.GOAL_OTHER,
            "assist": ScoutCalculator.points_system.ASSIST,
            "sem_gol": ScoutCalculator.points_system.SEM_GOL,
            "desarme": ScoutCalculator.points_system.TACKLE,
            "defesa": ScoutCalculator.points_system.DEFENSE,
            "cartao_amarelo": ScoutCalculator.points_system.YELLOW_CARD,
            "cartao_vermelho": ScoutCalculator.points_system.RED_CARD,
        }
    
    @staticmethod
    def estimate_ceiling(average: float, position: str) -> float:
        """Estima o teto (melhor case) de pontos para um jogador.
        
        Baseado na média + padrão de variação por posição.
        """
        # Multiplicador por posição (quanto pode variar para cima)
        position_multipliers = {
            "GOL": 1.3,
            "ZG": 1.4,
            "LD": 1.5,
            "LE": 1.5,
            "ZC": 1.4,
            "Vol": 1.6,
            "Mei": 1.7,
            "Ata": 1.8,  # Atacantes têm maior variação
        }
        
        multiplier = position_multipliers.get(position, 1.5)
        return average * multiplier
    
    @staticmethod
    def estimate_floor(average: float, consistency: float) -> float:
        """Estima o piso (pior case) de pontos para um jogador.
        
        Quanto menor a consistência, menor o piso.
        """
        # Multiplicador baseado em consistência
        consistency_pct = consistency / 100
        # Se 100% consist., piso é 70% da média
        # Se 50% consist., piso é 30% da média
        floor_pct = 0.3 + (consistency_pct * 0.4)
        return average * floor_pct
    
    @staticmethod
    def calculate_expected_value(
        average: float,
        position: str,
        consistency: float,
        opponent_strength: float = 0.5,
    ) -> float:
        """Calcula o valor esperado (EV) de um jogador em um confronto.
        
        Args:
            average: Média de pontos do jogador
            position: Posição do jogador
            consistency: Percentual de consistência
            opponent_strength: Força do adversário (0-1, onde 0.5 = neutro)
            
        Returns:
            Pontos esperados ajustados para o confronto
        """
        # Ajusta por força do adversário
        # Se adversário forte (0.8), esperado cai 20%
        # Se adversário fraco (0.2), esperado sobe 30%
        strength_adjustment = 1.0 - (opponent_strength * 0.5) + 0.25
        
        # Ajusta por consistência
        consistency_adjustment = consistency / 100
        
        # EV final
        ev = average * strength_adjustment * consistency_adjustment
        return ev
