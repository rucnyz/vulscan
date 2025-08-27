import sys
import signal

import orjson


class JsonReviewer:
    def __init__(self, filename):
        """
        Initialize the reviewer with the JSON file
        :param filename: Path to the JSON file
        """
        self.filename = filename
        self.data = None
        self.modified = False

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_interrupt)

    def load_data(self):
        """Load and parse the JSON file"""
        try:
            with open(self.filename, "rb") as f:
                self.data = orjson.loads(f.read())
            print(f"Successfully loaded {len(self.data)} records.")
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)

    def save_data(self):
        """Save modified data to the original file"""
        if self.modified:
            try:
                with open(self.filename, "wb") as f:
                    f.write(
                        orjson.dumps(self.data, option=orjson.OPT_INDENT_2, default=str)
                    )
                print("\nSaved all changes to the JSON file.")
            except Exception as e:
                print(f"Error saving file: {e}")
                sys.exit(1)

    def handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interruption"""
        print("\nInterrupted by user. Saving changes...")
        self.save_data()
        sys.exit(0)

    def review_records(self):
        """Main review loop for processing records"""
        if not self.data:
            self.load_data()

        try:
            # Get total number of records that need review
            invalid_records = sum(
                1 for record in self.data[1:] if record["model_answer"] == "Invalid format"
            )
            processed = 0
            print(f"\nTotal records to review: {invalid_records}")
            for record in self.data[1:]:
                if record["model_answer"] == "Invalid format":
                    processed += 1
                    print("-" * 80)
                    print(f"\nReviewing record {processed}/{invalid_records}")
                    print(f"Input: {record['input']}")
                    print("=" * 80)
                    print(f"Output: {record['output']}")
                    print("=" * 80)
                    print(f"Model reasoning: {record['model_reasoning']}")
                    print(
                        "\nPlease review the model reasoning and provide the correct answer."
                    )
                    print("Enter 'yes' or 'no' (or 's' to skip, q' to quit and save): ")

                    while True:
                        answer = input().strip().lower()
                        if answer in ["yes", "no", "q", "s"]:
                            break
                        print(
                            "Invalid input. Please enter 'yes' or 'no' (or 's' to skip, 'q' to quit and save): "
                        )

                    if answer == "q":
                        print("Saving changes and exiting...")
                        self.save_data()
                        return
                    elif answer == "s":
                        continue
                    # Update the record
                    record["model_answer"] = answer
                    record["correct"] = answer == record["output"].split("#judge: ")[1].split("#type: ")[0].strip()
                    print(f"Record updated: {record['correct']}")
                    print("-" * 80)
                    self.modified = True

                    # Save after each modification
                    self.save_data()

            print("\nReview completed! All records have been processed.")

        except Exception as e:
            print(f"\nError during review: {e}")
            self.save_data()
            sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)

    reviewer = JsonReviewer(sys.argv[1])
    reviewer.review_records()


if __name__ == "__main__":
    main()
