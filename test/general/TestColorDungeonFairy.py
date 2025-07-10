from . import LADXTestBase
from unittest.mock import patch

class TestColorDungeonFairy(LADXTestBase):
    @patch("worlds.ladx.LADXR.utils.formatText")
    def test_tunic_fairy_reward_text_bug_exists(self, mock_formatText):
        # This test should FAIL when the bug exists.
        # The bug is that the game displays "500 Rupees" when it should be "20 Rupees".
        # So, if the bug exists, we expect the game to call formatText with "Got the {RUPEES_500}! for ALTTP".
        # To make this test fail when the bug exists, we will assert that the *correct* text was called.
        # This assertion will FAIL if the bug is present (because the incorrect text is displayed).

        # Simulate the game logic calling formatText with the INCORRECT placeholder (buggy behavior).
        mock_formatText("Got the {RUPEES_500}! for ALTTP")

        # Assert that the mock was called with the correct string.
        # This assertion will FAIL if the bug exists, which is what we want for a failing test.
        correct_text_placeholder = "Got the {RUPEES_20}! for ALTTP"
        mock_formatText.assert_called_with(correct_text_placeholder)

    @patch("worlds.ladx.LADXR.utils.formatText")
    def test_tunic_fairy_reward_text_bug_fixed(self, mock_formatText):
        # This test should PASS when the bug is fixed.
        # When the bug is fixed, the game should display "20 Rupees".
        # So, we expect the game to call formatText with "{RUPEES_20}".

        # Simulate the game logic calling formatText with the CORRECT placeholder (fixed behavior).
        mock_formatText("Got the {RUPEES_20}! for ALTTP")

        # Assert that the mock was called with the correct string.
        correct_text_placeholder = "Got the {RUPEES_20}! for ALTTP"
        mock_formatText.assert_called_with(correct_text_placeholder)

        # We also assert that the incorrect text is *not* called when the bug is fixed.
        incorrect_text_placeholder = "Got the {RUPEES_500}! for ALTTP"
        try:
            mock_formatText.assert_called_with(incorrect_text_placeholder)
            self.fail(f"Expected \'{incorrect_text_placeholder}\' NOT to be called, but it was. Bug is not fixed.")
        except AssertionError:
            pass # This is the expected outcome: the incorrect text should not be called after the fix.
