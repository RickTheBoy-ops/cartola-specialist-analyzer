"""Orquestrador principal de análise."""

from typing import List, Optional
from .models import (
    Match,
    Player,
    ChecklistResponse,
    PostureEnum,
)
from .checklist import CartolaPrescalingChecklist
from .scouts import ScoutCalculator


class SpecialistAnalyzer:
    """Analisador especialista para Cartola FC.
    
    Orquestra o checklist completo de pré-escalação.
    """
    
    def __init__(self, rodada: int, budget: float = 100.0):
        self.rodada = rodada
        self.budget = budget
        self.checklist: Optional[CartolaPrescalingChecklist] = None
        self.response: Optional[ChecklistResponse] = None
        self.scout_calc = ScoutCalculator()
    
    def analyze(
        self,
        matches: List[Match],
        posture: PostureEnum = PostureEnum.MEIO_TERMO,
    ) -> ChecklistResponse:
        """Executa análise completa da rodada.
        
        Args:
            matches: Lista de partidas da rodada
            posture: Postura de escalação (mitar/valorizar/meio-termo)
            
        Returns:
            ChecklistResponse com resultado da análise
        """
        # Cria checklist
        self.checklist = CartolaPrescalingChecklist(
            rodada=self.rodada,
            budget=self.budget,
            posture=posture
        )
        
        # Carrega partidas
        self.checklist.load_matches(matches)
        
        # Executa todas as 6 etapas
        self.response = self.checklist.run()
        
        return self.response
    
    def get_report(self) -> str:
        """Retorna relatório markdown da análise."""
        if not self.checklist:
            return "Nenhuma análise foi executada."
        
        return self.checklist.get_report()
    
    def get_json_response(self) -> dict:
        """Retorna resposta em JSON."""
        if not self.response:
            return {}
        
        return self.response.dict()
