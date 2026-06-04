from dataclasses import dataclass

from app.services.relationship_state_service import RelationshipDelta


RULE_VERSION = "date-rule-v1"


@dataclass(frozen=True)
class DateChoice:
    choice_id: str
    label: str
    score: int


@dataclass(frozen=True)
class DateStep:
    sequence_no: int
    airi_line: str
    choices: list[DateChoice]


@dataclass(frozen=True)
class DateRuleResult:
    result: str
    score: int
    airi_reaction: str
    relationship_delta: RelationshipDelta
    reward_type: str
    reward_status: str


class DateEventRuleEngine:
    def first_step(self, event_code: str) -> DateStep:
        return self._steps(event_code)[0]

    def next_step(self, *, event_code: str, current_sequence_no: int) -> DateStep | None:
        steps = self._steps(event_code)
        next_index = current_sequence_no
        if next_index >= len(steps):
            return None
        return steps[next_index]

    def score_choice(self, *, event_code: str, sequence_no: int, choice_id: str) -> int:
        step = self._steps(event_code)[sequence_no - 1]
        for choice in step.choices:
            if choice.choice_id == choice_id:
                return choice.score
        raise ValueError("Unknown date event choice")

    def finish(self, *, event_code: str, score: int) -> DateRuleResult:
        if score >= 35:
            result = "success"
        elif score >= 20:
            result = "neutral"
        else:
            result = "failed"

        if event_code == "comfort_date":
            delta = RelationshipDelta(trust=4, affinity=1, familiarity=1) if result == "success" else RelationshipDelta(trust=2, affinity=1)
            reward_type = "voice" if result == "success" else "note"
            line = "I kept that moment carefully. We can come back to this when you need it."
        elif event_code == "weekend_plan":
            delta = RelationshipDelta(familiarity=3, affinity=2, trust=1) if result == "success" else RelationshipDelta(familiarity=2, affinity=1)
            reward_type = "note"
            line = "I wrote down the small promise we made for the weekend."
        else:
            delta = RelationshipDelta(affinity=3, familiarity=2, trust=1) if result == "success" else RelationshipDelta(affinity=2, familiarity=1)
            reward_type = "image" if result == "success" else "note"
            line = "That felt like a small movie scene between us."

        return DateRuleResult(
            result=result,
            score=score,
            airi_reaction=line,
            relationship_delta=delta,
            reward_type=reward_type,
            reward_status="pending" if result == "success" else "unlocked",
        )

    def _steps(self, event_code: str) -> list[DateStep]:
        if event_code == "comfort_date":
            return [
                DateStep(
                    sequence_no=1,
                    airi_line="How should I stay with you right now?",
                    choices=[
                        DateChoice("listen", "Just listen", 15),
                        DateChoice("encourage", "Encourage me", 12),
                        DateChoice("plan", "Help me make a small plan", 15),
                    ],
                ),
                DateStep(
                    sequence_no=2,
                    airi_line="What would make tonight a little easier?",
                    choices=[
                        DateChoice("quiet", "A quiet moment", 10),
                        DateChoice("warm_words", "Warm words", 15),
                    ],
                ),
            ]
        if event_code == "weekend_plan":
            return [
                DateStep(
                    sequence_no=1,
                    airi_line="What kind of weekend promise should we make?",
                    choices=[
                        DateChoice("walk", "A short walk", 12),
                        DateChoice("movie", "A movie night", 15),
                        DateChoice("rest", "A real rest day", 12),
                    ],
                ),
                DateStep(
                    sequence_no=2,
                    airi_line="How should I remember it?",
                    choices=[
                        DateChoice("diary", "Write it in an Airi note", 15),
                        DateChoice("reward", "Make it a tiny reward goal", 15),
                    ],
                ),
            ]
        return [
            DateStep(
                sequence_no=1,
                airi_line="What kind of movie mood should we pick?",
                choices=[
                    DateChoice("cozy", "Cozy and comfortable", 15),
                    DateChoice("funny", "Light and funny", 12),
                    DateChoice("deep", "Quiet and thoughtful", 15),
                ],
            ),
            DateStep(
                sequence_no=2,
                airi_line="Where should this little movie date happen?",
                choices=[
                    DateChoice("cinema", "A small cinema date", 15),
                    DateChoice("home", "A calm home movie night", 10),
                ],
            ),
        ]
