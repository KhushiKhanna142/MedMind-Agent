"""
Tool: Load benchmark answers for comparison
"""

from typing import List, Dict, Optional
import os
import json
import csv
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class BenchmarkLoader:
    """
    Load benchmark (correct) answers for clinical simulation questions.
    Supports multiple sources:
      1. Extract from question objects (correct_answer field)
      2. Load from JSON/CSV benchmark files
      3. Integrate with MedAgentGym if available
    """

    def __init__(self, config=None):
        """
        Initialize Benchmark Loader.

        Args:
            config: SimulationConfig instance (optional)
        """
        self.config = config
        self.benchmark_data_path = getattr(
            config, "benchmark_data_path", "data/benchmarks"
        ) if config else "data/benchmarks"

        os.makedirs(self.benchmark_data_path, exist_ok=True)
        self._benchmark_cache: Dict[str, Dict] = {}

        logger.info(
            "BenchmarkLoader initialized with path: %s",
            self.benchmark_data_path,
        )

    def load_benchmark_answers(
        self,
        questions: List[Dict],
        source: str = "auto",
    ) -> List[str]:
        """
        Load benchmark answers for the given question set.

        Args:
            questions: List of question dicts
            source: "auto", "questions", "file", or "medagentgym"

        Returns:
            List of benchmark answers aligned with questions
        """
        logger.info(
            "Loading benchmark answers for %d questions (source=%s)",
            len(questions),
            source,
        )

        if not questions:
            raise ValueError("No questions provided to load benchmarks")

        if source == "auto":
            source = self._determine_source(questions)

        if source == "questions":
            answers = self._load_from_questions(questions)
        elif source == "file":
            answers = self._load_from_file(questions)
        elif source == "medagentgym":
            answers = self._load_from_medagentgym(questions)
        else:
            logger.warning("Unknown source '%s'; defaulting to questions", source)
            answers = self._load_from_questions(questions)

        if len(answers) != len(questions):
            raise ValueError(
                f"Answer count mismatch: {len(answers)} answers for "
                f"{len(questions)} questions"
            )

        logger.info("✅ Loaded %d benchmark answers", len(answers))
        return answers

    # ------------------------------------------------------------------
    # Source helpers
    # ------------------------------------------------------------------
    def _determine_source(self, questions: List[Dict]) -> str:
        """Automatically pick the best benchmark source."""
        if all(q.get("correct_answer") for q in questions):
            logger.info("Using embedded correct_answer data")
            return "questions"

        if self._benchmark_file_exists(questions):
            logger.info("Benchmark file discovered; using file source")
            return "file"

        if self.config and getattr(self.config, "use_medagentgym", False):
            logger.info("MedAgentGym enabled; attempting integration")
            return "medagentgym"

        return "questions"

    def _load_from_questions(self, questions: List[Dict]) -> List[str]:
        """Extract answers from the question structures themselves."""
        answers: List[str] = []

        for idx, question in enumerate(questions):
            correct_answer = question.get("correct_answer")

            if not correct_answer:
                question_id = question.get("question_id", f"Q{idx+1}")
                logger.warning(
                    "Question %s missing correct_answer; attempting to infer",
                    question_id,
                )
                correct_answer = self._extract_answer_from_options(question)

            if not correct_answer:
                raise ValueError(
                    f"Question {question.get('question_id', idx)} has no "
                    "correct_answer and cannot be inferred"
                )

            answers.append(self._normalize_answer(correct_answer, question))

        return answers

    def _extract_answer_from_options(self, question: Dict) -> Optional[str]:
        """
        Attempt to reconstruct the answer from MCQ options + metadata.
        """
        options = question.get("options", [])
        metadata = question.get("metadata", {})
        answer_letter = metadata.get("answer_letter") or metadata.get("correct_option")

        if answer_letter and options:
            letter = answer_letter.strip().upper()
            for option in options:
                option_str = option.strip()
                if option_str.startswith(f"{letter})") or option_str.startswith(f"{letter}."):
                    return option

        return None

    def _normalize_answer(self, answer: str, question: Dict) -> str:
        """
        Normalize the answer text for consistent comparison downstream.
        """
        answer_stripped = answer.strip()

        if len(answer_stripped) == 1 and answer_stripped.isalpha():
            letter = answer_stripped.upper()
            for option in question.get("options", []):
                opt = option.strip()
                if opt.startswith(f"{letter})") or opt.startswith(f"{letter}."):
                    return opt

        return answer

    def _load_from_file(self, questions: List[Dict]) -> List[str]:
        """Load benchmarks from JSON/CSV files on disk."""
        benchmark_file = self._find_benchmark_file(questions)

        if not benchmark_file:
            raise FileNotFoundError(
                f"No benchmark file found in {self.benchmark_data_path}"
            )

        ext = Path(benchmark_file).suffix.lower()
        if ext == ".json":
            benchmark_map = self._load_json_benchmark(benchmark_file)
        elif ext == ".csv":
            benchmark_map = self._load_csv_benchmark(benchmark_file)
        else:
            raise ValueError(f"Unsupported benchmark file format: {ext}")

        answers: List[str] = []
        for question in questions:
            qid = question.get("question_id")
            if qid in benchmark_map:
                answers.append(benchmark_map[qid])
            else:
                logger.warning(
                    "Question %s missing in benchmark file; falling back to question data",
                    qid,
                )
                answers.append(
                    self._normalize_answer(
                        question.get("correct_answer", ""),
                        question,
                    )
                )

        return answers

    def _find_benchmark_file(self, questions: List[Dict]) -> Optional[str]:
        """Discover the most suitable benchmark file for this run."""
        benchmark_path = Path(self.benchmark_data_path)
        if not benchmark_path.exists():
            return None

        domains = set(q.get("domain", "general") for q in questions)
        domain_tag = (
            "_".join(sorted(domains))
            if domains and len(domains) <= 2
            else "multi_domain"
        )

        candidates = [
            benchmark_path / "benchmarks.json",
            benchmark_path / "benchmarks.csv",
            benchmark_path / f"{domain_tag}_benchmarks.json",
            benchmark_path / f"{domain_tag}_benchmarks.csv",
        ]

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        for candidate in benchmark_path.glob("*.json"):
            return str(candidate)
        for candidate in benchmark_path.glob("*.csv"):
            return str(candidate)

        return None

    def _load_json_benchmark(self, file_path: str) -> Dict[str, str]:
        """Parse benchmark answers from JSON."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            benchmarks = data
        else:
            benchmarks = {}
            for item in data:
                qid = item.get("question_id") or item.get("id")
                ans = item.get("answer") or item.get("correct_answer")
                if qid and ans:
                    benchmarks[qid] = ans

        logger.info("Loaded %d benchmarks from JSON", len(benchmarks))
        return benchmarks

    def _load_csv_benchmark(self, file_path: str) -> Dict[str, str]:
        """Parse benchmark answers from CSV."""
        benchmarks: Dict[str, str] = {}

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row.get("question_id") or row.get("id")
                ans = row.get("answer") or row.get("correct_answer")
                if qid and ans:
                    benchmarks[qid] = ans

        logger.info("Loaded %d benchmarks from CSV", len(benchmarks))
        return benchmarks

    def _benchmark_file_exists(self, questions: List[Dict]) -> bool:
        """Boolean helper to check if any benchmark file is available."""
        return self._find_benchmark_file(questions) is not None

    def _load_from_medagentgym(self, questions: List[Dict]) -> List[str]:
        """Load benchmark answers via MedAgentGym integration."""
        try:
            from .medagentgym_integration import MedAgentGymIntegration

            medagentgym = MedAgentGymIntegration(self.config)
            answers = medagentgym.get_benchmark_answers(questions)
            logger.info("Loaded %d benchmarks from MedAgentGym", len(answers))
            return answers
        except ImportError:
            logger.warning(
                "MedAgentGym integration not available; falling back to questions"
            )
            return self._load_from_questions(questions)
        except Exception as exc:
            logger.error(
                "MedAgentGym fetch failed (%s); falling back to questions",
                exc,
            )
            return self._load_from_questions(questions)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def save_benchmark_file(
        self,
        questions: List[Dict],
        file_path: Optional[str] = None,
        fmt: str = "json",
    ) -> str:
        """
        Persist benchmark answers for future reuse.

        Args:
            questions: Question list with correct_answer data
            file_path: Optional explicit file path
            fmt: "json" or "csv"
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                self.benchmark_data_path,
                f"benchmarks_{timestamp}.{fmt}",
            )

        benchmark_map = {
            q.get("question_id", f"Q{i+1}"): q.get("correct_answer", "")
            for i, q in enumerate(questions)
        }

        if fmt == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(benchmark_map, f, indent=2, ensure_ascii=False)
        elif fmt == "csv":
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["question_id", "answer"])
                for qid, ans in benchmark_map.items():
                    writer.writerow([qid, ans])
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        logger.info("Saved %d benchmarks to %s", len(benchmark_map), file_path)
        return file_path

