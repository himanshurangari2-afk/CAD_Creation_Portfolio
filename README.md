# CAD Lead Generation Assistant

This repository now includes a lightweight lead-generation assistant for a CAD / drafting business.

It is designed for a safe, review-first workflow:

- read business leads from CSV
- score them by relevance to CAD / manufacturing / drafting work
- generate a personalized outreach message
- keep a reviewed output file for approved leads
- optionally send emails via SMTP if credentials are configured
- generate WhatsApp message links from phone numbers

This is an MVP for your business and is meant to support manual approval before sending outreach.

## Quick start

1. Review `sample_leads.csv`
2. Run:

   python lead_agent.py --input sample_leads.csv --output approved_leads.csv

3. Review the generated message drafts in `approved_leads.csv`
4. If you want to send emails, configure SMTP environment variables and run:

   python lead_agent.py --input sample_leads.csv --output approved_leads.csv --send-email

## Required environment variables for SMTP

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SENDER_EMAIL`
- `EMAIL_SUBJECT_PREFIX` (optional)

Example:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SENDER_EMAIL=your-email@gmail.com
```

## CSV format

Use this structure in your CSV file:

```csv
company_name,industry,city,phone,email,website,notes
Precision Fabrication Works,Fabrication,Nagpur,+919876543210,sales@precisionfab.in,https://precisionfab.in,Sheet metal and custom fabrication
```

## What the script does

- filters leads to CAD-relevant businesses
- assigns a score from 1 to 100
- picks the best outreach angle per business category
- creates a message tailored to the lead type
- exports a final document with lead details and text draft

## Safe usage note

This script does not spam. It is intended for professional outreach to relevant local businesses and should be used with care and compliance with local laws and platform policies.

## Portfolio

Your portfolio page is here:

https://himanshurangari2-afk.github.io/CAD_Creation_Portfolio/
