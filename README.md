# secret-santa-assigner

# Purpose:
  With the coronavirus causing all things to go virtual, I realized that a traditional secret-santa between famailies may not be able to be drawn from a hat! In order to keep the true anonymous purpose of secret santa, we can't have one person choose a random assignee for each person participating in the Secret Santa as they would then know who was assigned to who.

This small project solves that issue.

# Usage:
    1. Clone the repository
    2. Create a virtual Python environment
    3. Install the required packages through the requirements.txt
    4. Run the main.py with --setup-twilio argument, this will authenticate you with your Twilio account (https://www.twilio.com/console).
    5. Fill in the details on input.csv
      Example:
        name,phone
        john,+155555555555
     6. Run main.py without arguments to be prompted.
     NOTE: Use arg: --dry-run to confirm the messages are correct before sending.
