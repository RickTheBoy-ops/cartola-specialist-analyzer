"""Modelos de dados para análise de Cartola FC."""

from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class PostureEnum(str, Enum):
    """Postura de escalação: agressiva (mitar), conservadora (valorizar) ou meio-termo."""
    MITAR = "mitar"  # Alto risco, busca jogadores baratos com alto potencial
    VALORIZAR = "valorizar"  # Baixo risco, foca em jogadores seguros com chance de subir preço
    MEIO_TERMO = "meio_termo"  # Balançeado entre segurança e oportunidade


class RiskProfile(str, Enum):
    """Perfil de risco de um jogador."""
    BAIXO = "baixo"  # Lesionado, suspenso ou muito inconsistente
    MODERADO = "moderado"  # Volta de lesão, desfalque recente, sequência incerta
    ALTO = "alto"  # Jogando bem, em forma, escalado em muitas rodadas
    MUDAR_POSICAO = "mudar_posicao"  # Risco tático: joga diferente da posição


class Scout(BaseModel):
    """Representa um scout individual (gol, assiste, SG, etc)."""
    name: str  # ex: "gol", "assist", "SG", "desarme", "defesa"
    points: float  # pontos que vale no Cartola
    average: float = Field(default=0.0, description="Média da rodada do jogador")
    last_5_matches: List[float] = Field(default_factory=list, description="Scouts das últimas 5 rodadas")


class Player(BaseModel):
    """Modelo de jogador com todos os dados necessários para análise."""
    player_id: int
    name: str
    position: str  # "GOL", "ZG", "LD", "LE", "ZC", "Vol", "Mei", "Ata"
    team: str  # Nome do time
    price: float  # Preço atual (milhões)
    price_change: float = Field(default=0.0, description="Variação de preço na rodada")
    average_points: float  # Média de pontos por rodada
    scouts: List[Scout] = Field(default_factory=list)  # Scouts desse jogador
    consistency: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentual de rodadas jogadas")
    matches_played: int = Field(default=0, description="Rodadas jogadas")
    minutes_played: int = Field(default=0, description="Minutos totais")
    status: str = Field(default="Disponível")  # "Lesionado", "Suspenso", "Provvel"
    risk_profile: RiskProfile = Field(default=RiskProfile.ALTO)
    
    # Campos derivados (calculados)
    mpv: Optional[float] = Field(default=None, description="Mínimo Para Valorizar")
    expected_points: Optional[float] = Field(default=None, description="Pontos esperados vs próximo adversário")
    ceiling: Optional[float] = Field(default=None, description="Melhor caso: max pontos possível")
    floor: Optional[float] = Field(default=None, description="Pior caso: min pontos possível")


class Team(BaseModel):
    """Modelo de time."""
    team_id: int
    name: str
    players: List[Player] = Field(default_factory=list)
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Força relativa do time (0-1)")
    home: bool = Field(default=False, description="Joga em casa nessa rodada?")
    goals_expected: float = Field(default=0.0, description="Gols esperados (xG)")
    goals_conceded_expected: float = Field(default=0.0, description="Gols contra esperados (xGA)")
    recent_form: float = Field(default=0.5, ge=0.0, le=1.0, description="Forma recente (0-1)")


class Match(BaseModel):
    """Modelo de partida."""
    match_id: int
    rodada: int
    home_team: Team
    away_team: Team
    probability_home_win: float = Field(default=0.33, description="Probabilidade de vitória do time da casa")
    probability_draw: float = Field(default=0.33, description="Probabilidade de empate")
    probability_away_win: float = Field(default=0.33, description="Probabilidade de vitória do visitante")
    over_25_goals: float = Field(default=0.5, description="Probabilidade de +2.5 gols na partida")
    expected_goals: float = Field(default=2.5, description="Gols totais esperados")
    kick_off: datetime
    status: str = Field(default="scheduled")  # "scheduled", "live", "finished"


class AnalysisStep(BaseModel):
    """Representa uma etapa da análise do checklist."""
    step_number: int
    step_name: str
    completed: bool = False
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ChecklistResponse(BaseModel):
    """Resposta completa do checklist pré-escalação."""
    rodada: int
    timestamp: datetime
    budget: float
    posture: PostureEnum
    
    # 6 etapas do checklist
    step1_leitura_rodada: AnalysisStep
    step2_patrimonio: AnalysisStep
    step3_scouts: AnalysisStep
    step4_contexto: AnalysisStep
    step5_gestao_risco: AnalysisStep
    step6_capitao: AnalysisStep
    
    # Resultado final
    recommended_players: List[Player] = Field(default_factory=list)
    recommended_captain: Optional[Player] = None
    estimated_score: Optional[float] = None
    risk_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Score de risco geral (0=baixo, 1=alto)")
    confidence_level: float = Field(default=0.0, ge=0.0, le=100.0, description="Confiança na escalação (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rodada": 38,
                "budget": 100.0,
                "posture": "meio_termo",
                "confidence_level": 85.0
            }
        }
