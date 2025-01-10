# ReportBotThing

ReportBotThing is a Discord bot designed to assist moderation teams by providing functionality to report messages or users and manage those reports efficiently. This bot is tailored for use in **a single server** and allows for customization of report messages and settings.

---

## Features

- **Report Messages**: Context menu to report specific messages.
- **Report Users**: Context menu to report users.
- **Customizable Reports**: Modify report messages and settings using commands.
- **Management**: Reactivate or deactivate reports as needed.
- **Database Integration**: Stores reports in a SQLite database for persistence.

---

## File Structure

- `main.py`: Entry point of the bot.
- `cogs/`: Contains various bot functionalities split into different files.
  - `aReportStringCustomization.py`: Allows customization of report strings.
  - `bReportCustomizationHelp.py`: Provides a help interface for customizing reports.
  - `cEditReports.py`: Commands to edit report configurations.
  - `dchangeActivationStatusReports.py`: Commands to activate or deactivate reports.
- `.env`: Stores bot token and other sensitive information.
- `ctx.py`: Defines context menu actions for reporting.
- `models.py`: Database models and session management.
- `reports.json`: Configuration file for report settings.
- `util.py`: Utility functions and environment management.

---

## Requirements

- Python 3.11.9.
- The contents of `requirements.txt`.

---

## Setup

1. Clone the repository to your local machine.
2. Install the required libraries using:

   ```bash
   pip install -r requirements.txt
    ```

3. Create a new Discord bot and obtain the token.
4. Create a `.env` file in the root directory and add the contents of `.env.example` with your bot token and other information.
5. Run the bot using:

   ```bash
   python main.py
   ```

---

## Customization

To customize the report messages and settings, modify the `reports.json` file or use the commands provided by the bot. The `reports.json` file contains the following customizable fields:

- `title-message`
- `title-user`
- `description-message`
- `description-user`
- `color`
- `claimed_color`
- `resolved_color`
- `max_reason_length`
- `user_report_timeout`
- `message_report_message`
- `user_report_message`
- `duplicate_user_report_message`
- `duplicate_message_report_message`
- `report_failure_message`
- `report_modal_reason_label`
- `report_modal_reason_placeholder`
- `duplicate_report_modal_reason_label`
- `duplicate_report_modal_reason_placeholder`

Use reportHelp and customizeReports to view the available customization commands.

---
