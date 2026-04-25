import os
import time
import random
from datetime import datetime
import sys  # Needed for proper exit on failure

LOG_FILE = "build_report.txt"

class BuildProcess:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.failed_steps = []  # Track failed steps

    def add_step(self, step_name):
        self.steps.append(step_name)

    def run(self):
        print(f"Starting build process: {self.name}")
        self.log(f"Build started at {datetime.now()}")

        for index, step in enumerate(self.steps, start=1):
            print(f"\nStep {index}: {step}")
            success = self.execute_step(step)
            if not success:
                self.failed_steps.append(step)

        self.log(f"Build finished at {datetime.now()}")

        if self.failed_steps:
            print(f"\nBuild completed with failures: {len(self.failed_steps)} failed steps")
        else:
            print("\nBuild completed successfully!")

    def execute_step(self, step):
        print(f"Executing {step} ...")
        time.sleep(1)

        # Simulate random success/failure
        result = random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILURE"])

        if result == "SUCCESS":
            print(f"{step} finished successfully")
            self.log(f"{step}: SUCCESS")
            return True
        else:
            print(f"{step} failed")
            self.log(f"{step}: FAILURE")
            return False

    def log(self, message):
        with open(LOG_FILE, "a") as f:
            f.write(message + "\n")

def cleanup_old_logs():
    if os.path.exists(LOG_FILE):
        size = os.path.getsize(LOG_FILE)
        print(f"Old log file size: {size} bytes")
    else:
        print("No old logs found.")

def generate_summary():
    print("\nGenerating summary...")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

        success = sum(1 for l in lines if "SUCCESS" in l)
        failure = sum(1 for l in lines if "FAILURE" in l)

        print(f"Summary:")
        print(f" Successful steps: {success}")
        print(f" Failed steps: {failure}")
    else:
        print("No log file to summarize.")

def main():
    print("====================================")
    print(" Jenkins Python Build Simulation ")
    print("====================================")

    cleanup_old_logs()

    build = BuildProcess("Sample-Python-Build")

    build.add_step("Checkout Code")
    build.add_step("Install Dependencies")
    build.add_step("Run Unit Tests")
    build.add_step("Static Code Analysis")
    build.add_step("Package Application")
    build.add_step("Deploy Application")
    build.add_step("Dummy Step")  # Optional step included in build
    #skkskmxksmkxmsmx
    #This is the commit for jenkins....

    build.run()
    generate_summary()

    # Exit with failure if any step failed
    if build.failed_steps:
        sys.exit(1)  # Only exit if there were failures

if __name__ == "__main__":
    main()
