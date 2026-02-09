# WhatsApp Sender — Python + Selenium

## Overview

Automate sending personalized WhatsApp messages via WhatsApp Web using Python and Selenium. This project grew out of a quick productivity hack: I needed to send personalized messages to 21+ people and turned a repetitive 30+ minute task into a 5-minute automated one.

Two post styles are included below (long and short) to use as social copy or project description.

## Features

- Sends personalized messages to individual contacts (not groups)
- Maintains configurable delays to reduce the chance of spam detection
- Basic error handling and logging to handle failed deliveries
- Minimal setup: Python + Selenium + Chrome/Edge driver

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install Selenium directly:

```bash
pip install selenium
```

2. Download the browser driver matching your browser and OS (e.g., ChromeDriver for Chrome) and ensure it's on your PATH.

3. Open the script [whatsapp_sender.py](whatsapp_sender.py) and configure your contacts and message template. Typical configuration points:

- `contacts` or a `contacts.csv` file (phone numbers and names)
- `message_template` supporting placeholders like `{name}` for personalization
- `delay_seconds` and `per_message_delay` to tune timing

4. Run the script:

```bash
python whatsapp_sender.py
```

5. When the browser opens, scan the WhatsApp Web QR code (if not already logged in). The script will send messages to configured recipients, applying personalization and delays.

## Example Post Content (Long)

**🤖 Automating the Mundane: When Manual Work Meets Code**

Ever caught yourself doing repetitive tasks and thought, "Wait, I'm a tech person... why am I doing this manually?"

That's exactly what happened to me yesterday. 📱

I needed to send personalized WhatsApp messages to 21+ people individually (not in a group - everyone deserves a personal touch!). After manually sending messages to 3-4 contacts, I stopped and asked myself: "Why am I doing this the hard way?"

**The Solution?**
Built a Python automation script using Selenium to send WhatsApp messages through WhatsApp Web. The script:
✅ Sends personalized messages to each contact individually
✅ Maintains proper delays to avoid spam detection
✅ Handles errors gracefully
✅ Saves hours of manual work

**The Result?**
What would've taken me 30+ minutes of repetitive copy-pasting was done in less than 5 minutes (after the initial 10 minutes of coding, of course! 😄)

This is what I love about being in tech - the ability to automate the mundane and focus on what truly matters.

📹 Check out the video below to see it in action! (Blurred for privacy, of course)

**Key Takeaway:** If you find yourself doing something repetitive more than 3 times, there's probably a way to automate it. Don't be afraid to write that script!

#Automation #Python #Selenium #ProductivityHacks #CodingLife #TechLife #WhatsAppAutomation

## Short Version (Concise)

**🚀 From Manual to Automated in 10 Minutes**

Needed to send personalized WhatsApp messages to 21 people. After manually doing 3-4, I realized: "I'm a developer... why am I doing this manually?"

10 minutes later → Python + Selenium script ready ✅
Result → 30 minutes of work done in 5 minutes

This is why I love coding - turning repetitive tasks into automated solutions! 💻

📹 Video below (blurred for privacy)

#Python #Automation #Selenium #ProductivityHacks #DeveloperLife

## Configuration Tips

- Keep message templates short and human.
- Add a per-message delay of several seconds to mimic human behavior.
- Use personalization placeholders like `{name}` and validate inputs.
- Avoid sending to recipients who haven't consented.

## Troubleshooting

- "Element not found": increase delays or update selectors (WhatsApp Web UI can change).
- Driver/binary mismatch: ensure your browser driver matches your browser version.
- Login issues: make sure you scan the QR code and keep the session active.

## Safety & Ethics

Automating messaging can cross into spam or violate service terms. Use this script responsibly:

- Only message consenting recipients.
- Respect rate limits and add delays.
- Do not use for unsolicited mass marketing.

## License

This project is provided as-is for personal productivity and learning. Adapt or add a license as needed for your use.

---

If you'd like, I can also:
- Add a `requirements.txt` and a sample `contacts.csv`
- Add CLI options to `whatsapp_sender.py` for message file and delay tuning
- Create a short demo GIF (blurred) and include it in this README

Feel free to tell me which follow-up you'd like.
