import unittest
from core.rhythm_exercises import (
    RHYTHM_EXERCISES,
    RhythmPattern_Exercise,
    get_exercises_by_level,
    get_exercise_by_id,
)

VALID_TIME_SIGNATURES = {"4/4", "3/4", "6/8"}


def measure_beats(time_signature: str) -> float:
    """Nº de tempos (em semínimas) de uma medida: 4/4 -> 4, 3/4 -> 3, 6/8 -> 3."""
    n, d = time_signature.split("/")
    return float(n) * (4.0 / float(d))


class TestRhythmExercises(unittest.TestCase):
    def test_exercise_count(self):
        self.assertGreaterEqual(len(RHYTHM_EXERCISES), 8, "Deve haver pelo menos 8 padrões rítmicos")

    def test_exercise_fields_validity(self):
        for ex in RHYTHM_EXERCISES:
            self.assertIsInstance(ex, RhythmPattern_Exercise)
            self.assertTrue(ex.id, f"{ex.id}: id vazio")
            self.assertTrue(ex.name_pt)
            self.assertTrue(ex.name_en)
            self.assertIn(ex.level, [1, 2, 3, 4, 5], f"{ex.id}: nível inválido {ex.level}")
            self.assertIn(ex.time_signature, VALID_TIME_SIGNATURES,
                          f"{ex.id}: compasso inválido {ex.time_signature}")
            self.assertTrue(ex.description_pt)
            self.assertTrue(ex.description_en)
            self.assertGreater(len(ex.durations), 0, f"{ex.id}: sem durações")
            self.assertTrue(all(d > 0 for d in ex.durations),
                            f"{ex.id}: durações devem ser positivas")

    def test_durations_fill_the_measure(self):
        """Regressão: a soma das durações tem de igualar os tempos da medida.

        Um padrão em 4/4 tem de somar 4 tempos; em 3/4, 3; em 6/8, 3 (6 colcheias).
        """
        for ex in RHYTHM_EXERCISES:
            expected = measure_beats(ex.time_signature)
            self.assertAlmostEqual(
                sum(ex.durations), expected, delta=1e-6,
                msg=f"{ex.id} ({ex.time_signature}): soma {sum(ex.durations)} != {expected} tempos",
            )

    def test_total_beats_property(self):
        for ex in RHYTHM_EXERCISES:
            self.assertAlmostEqual(ex.total_beats, sum(ex.durations), delta=1e-6)

    def test_levels_1_to_5_all_present(self):
        for level in [1, 2, 3, 4, 5]:
            self.assertGreaterEqual(
                len(get_exercises_by_level(level)), 1,
                f"Não há nenhum padrão de nível {level}",
            )

    def test_get_exercises_by_level_filters(self):
        for level in [1, 2, 3, 4, 5]:
            exs = get_exercises_by_level(level)
            self.assertTrue(all(e.level == level for e in exs),
                            f"get_exercises_by_level({level}) devolveu outro nível")

    def test_get_exercise_by_id(self):
        first = RHYTHM_EXERCISES[0]
        self.assertEqual(get_exercise_by_id(first.id).id, first.id)
        self.assertIsNone(get_exercise_by_id("nao_existe"))

    def test_time_signatures_not_all_44(self):
        """Para não ficar tudo em 4/4 (pedido na spec)."""
        sigs = {ex.time_signature for ex in RHYTHM_EXERCISES}
        self.assertGreaterEqual(len(sigs), 3, f"Faltam compassos variados: {sigs}")
        self.assertIn("3/4", sigs)
        self.assertIn("6/8", sigs)

    def test_i18n_getters(self):
        ex = RHYTHM_EXERCISES[0]
        self.assertEqual(ex.get_name("pt"), ex.name_pt)
        self.assertEqual(ex.get_name("en"), ex.name_en)
        self.assertEqual(ex.get_description("pt"), ex.description_pt)
        self.assertEqual(ex.get_description("en"), ex.description_en)


if __name__ == "__main__":
    unittest.main()
