import json
from pathlib import Path
from typing import Type

import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


RAI_CONTEXT_PATH = r"C:\Users\keahn\Documents\UofT\Coursework\MIE1624\Project\rai_analysis\outputs\rai_context.json"
CSV_DIR = r"C:\Users\keahn\Documents\UofT\Coursework\MIE1624\Project\rai_analysis\data\processed"


class QueryInput(BaseModel):
    query: str = Field(..., description="A natural-language question or keyword to look up.")


class ProjectContextTool(BaseTool):
    """Returns the full structured project database as JSON, covering all analytical sections."""

    name: str = "Project Context Database"
    description: str = (
        "Returns the full structured project analysis database covering all sections: "
        "RAI scores and country rankings, R&D indicators, economy data, policy governance, "
        "and all three policy recommendations with costs and timelines for 13 countries. "
        "Use this for any question about specific scores, rankings, methodology, or "
        "cross-country comparisons."
    )
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        path = Path(RAI_CONTEXT_PATH)
        if not path.exists():
            return f"Project context file not found at: {RAI_CONTEXT_PATH}"
        with open(path, encoding="utf-8") as f:
            return json.dumps(json.load(f), indent=2)


class DataQueryTool(BaseTool):
    """Queries the project processed CSV tables using pandas for live statistical comparisons."""

    name: str = "Project CSV Data Query"
    description: str = (
        "Query the raw project CSV data tables for live statistical comparisons across "
        "all analytical sections. Available data: composite scores by country, policy "
        "participation by framework (OECD, CoE_Convention, EU_AI_Act, etc.), KPMG AI "
        "literacy ranks, RAI research papers by country, and external indices. "
        "Input examples: 'top 5 countries by composite score', 'Canada policy score', "
        "'bottom 3 countries by literacy', 'all countries'. "
        "Returns a formatted table of results."
    )
    args_schema: Type[BaseModel] = QueryInput

    def _run(self, query: str) -> str:
        csv_dir = Path(CSV_DIR)
        if not csv_dir.exists():
            return f"CSV directory not found at: {CSV_DIR}"

        composite = pd.read_csv(csv_dir / "composite_rai_scores.csv")
        policy = pd.read_csv(csv_dir / "policy_participation.csv")
        kpmg = pd.read_csv(csv_dir / "kpmg_ai_literacy.csv")

        policy_cols = ["country", "policy_score"]
        merged = composite.merge(policy[policy_cols], on="country", how="left")
        merged = merged.merge(kpmg, on="country", how="left")

        q = query.lower()

        if any(country in q for country in merged["country"].str.lower().tolist()):
            matched = merged["country"].str.lower().apply(lambda c: c in q)
            result = merged[matched]
        elif "top" in q or "best" in q or "highest" in q:
            n = 5
            for word in q.split():
                if word.isdigit():
                    n = int(word)
                    break
            result = merged.nlargest(n, "composite_rai_score")
        elif "bottom" in q or "lowest" in q or "worst" in q:
            n = 5
            for word in q.split():
                if word.isdigit():
                    n = int(word)
                    break
            result = merged.nsmallest(n, "composite_rai_score")
        elif "policy" in q:
            result = merged[["country", "policy_score"]].sort_values("policy_score", ascending=False)
        elif "literacy" in q or "kpmg" in q:
            result = merged[["country", "kpmg_rank"]].dropna().sort_values("kpmg_rank")
        elif "research" in q or "paper" in q:
            result = merged[["country", "rai_papers_2024", "rai_rank"]].sort_values("rai_papers_2024", ascending=False)
        else:
            result = merged[["country", "composite_rai_score", "rai_rank", "policy_score", "kpmg_rank"]]

        return result.to_string(index=False)
