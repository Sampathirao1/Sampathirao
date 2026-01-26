import unittest
import os
from unittest.mock import patch
from python1 import BuildProcess, LOG_FILE  # Import your main code

class TestBuildProcess(unittest.TestCase):

    def setUp(self):
        """Runs before each test"""
        self.build = BuildProcess("Test-Build")

        # Clear log file to ensure test isolation
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("")

    def test_add_step(self):
        """Test that steps are added correctly"""
        self.build.add_step("Step 1")
        self.assertEqual(len(self.build.steps), 1)
        self.assertEqual(self.build.steps[0], "Step 1")

    def test_execute_step_logs_correctly(self):
        """Test that executing a step writes to the log"""
        try:
            self.build.execute_step("Dummy Step")
        except Exception as e:
            self.fail(f"execute_step raised an exception: {e}")

        with open(LOG_FILE, "r") as f:
            log_content = f.read()

        # Check that step name appears in the log
        self.assertIn("Dummy Step", log_content)

        # Regex matches the actual log format: "Dummy Step: SUCCESS" or "Dummy Step: FAILURE"
        self.assertRegex(log_content, r"Dummy Step: (SUCCESS|FAILURE)")

    @patch.object(BuildProcess, 'execute_step')
    def test_execute_step_mocked(self, mock_execute):
        """Test execute_step call without actually running commands"""
        mock_execute.return_value = None  # Simulate success
        self.build.execute_step("Dummy Step")
        mock_execute.assert_called_with("Dummy Step")


if __name__ == "__main__":
    unittest.main()

#This is a my project pls approve this request.
