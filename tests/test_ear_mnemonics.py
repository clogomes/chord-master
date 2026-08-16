import unittest
from core.ear_mnemonics import EAR_MNEMONICS

class TestEarMnemonics(unittest.TestCase):
    def test_all_12_intervals_have_entries(self):
        # 12 intervals plus P1
        expected_codes = ["P1", "m2", "M2", "m3", "M3", "P4", "TT", "P5", "m6", "M6", "m7", "M7", "P8"]
        for code in expected_codes:
            self.assertIn(code, EAR_MNEMONICS)
            mnemonic = EAR_MNEMONICS[code]
            self.assertTrue(len(mnemonic.songs_ascending) > 0, f"Mnemonic songs_ascending for {code} is empty")
            self.assertTrue(len(mnemonic.songs_descending) > 0, f"Mnemonic songs_descending for {code} is empty")
            self.assertTrue(len(mnemonic.description) > 0, f"Mnemonic description for {code} is empty")
            self.assertTrue(len(mnemonic.description_en) > 0, f"Mnemonic description_en for {code} is empty")

if __name__ == "__main__":
    unittest.main()
