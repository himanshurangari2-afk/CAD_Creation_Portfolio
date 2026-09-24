#!/usr/bin/env python3
import argparse
import csv
import os
import re
from dataclasses import dataclass, asdict
from email.message import EmailMessage
from typing import List, Dict
from urllib.parse import quote_plus
import smtplib


RISK_WORDS = {
    "manufacturing", "fabrication", "mechanical", "machining", "architectural",
    "interior", "construction", "product", "prototype", "steel", "metal",
    "tooling", "engineering", "design", "cnc", "cad", "3d", "drawing",
    "drafting", "builder", "structural"
}


@dataclass
class Lead:
    company_name: str
    industry: str
    city: str
    phone: str
    email: str
    website: str
    notes: str
    lead_score: int = 0
    lead_type: str = ""
    message: str = ""
    whatsapp_link: str = ""
    status: str = "pending"


def normalize(value):
    if value is None:
        return ""
    return str(value).strip()


def detect_lead_type(lead: Dict[str, str]) -> str:
    text = " ".join([
        normalize(lead.get("company_name", "")),
        normalize(lead.get("industry", "")),
        normalize(lead.get("notes", "")),
    ]).lower()

    if any(keyword in text for keyword in ["fabrication", "machining", "manufacturing", "cnc", "metal", "steel", "tooling"]):
        return "fabrication"
    if any(keyword in text for keyword in ["architect", "interior", "construction", "building", "structural"]):
        return "architecture"
    if any(keyword in text for keyword in ["3d", "prototype", "product", "design", "engineering"]):
        return "product_design"
    if any(keyword in text for keyword in ["design", "cad", "drafting", "drawing"]):
        return "general_design"
    return "general_business"


def score_lead(lead: Dict[str, str]) -> int:
    text = " ".join([
        normalize(lead.get("company_name", "")),
        normalize(lead.get("industry", "")),
        normalize(lead.get("notes", "")),
    ]).lower()

    score = 0
    for word in RISK_WORDS:
        if word in text:
            score += 8

    if normalize(lead.get("website", "")):
        score += 8
    if normalize(lead.get("email", "")):
        score += 7
    if normalize(lead.get("phone", "")):
        score += 7
    if normalize(lead.get("city", "")):
        score += 5

    return min(score, 100)


def build_message(lead: Dict[str, str]) -> str:
    company = normalize(lead.get("company_name", "your business")) or "your business"
    city = normalize(lead.get("city", "your city"))
    lead_type = detect_lead_type(lead)
    website = normalize(lead.get("website", ""))
    website_text = f"Portfolio: {website}\n" if website else ""

    if lead_type == "fabrication":
        return (
            f"Hello,\n\n"
            f"I noticed {company} is working in fabrication / manufacturing services in {city}.\n\n"
            f"I provide CAD drafting, manufacturing drawings, 2D/3D detailing, and design support for fabrication and production teams.\n\n"
            f"{website_text}"
            f"If you have upcoming design, drawing conversion, or prototype support needs, I would be happy to help with accurate CAD work.\n\n"
            f"Best regards,\nHimanshu Rangari"
        )

    if lead_type == "architecture":
        return (
            f"Hello,\n\n"
            f"I came across {company} in {city} and wanted to connect regarding your architectural / construction design work.\n\n"
            f"I provide CAD drafting, layout detailing, floor plans, and documentation support for design and execution teams.\n\n"
            f"{website_text}"
            f"If you need drafting support or fast drawing turnaround, I’d be glad to assist.\n\n"
            f"Best regards,\nHimanshu Rangari"
        )

    if lead_type == "product_design":
        return (
            f"Hello,\n\n"
            f"I noticed {company} works in product design / engineering related work in {city}.\n\n"
            f"I provide CAD modeling, 3D design support, product detailing, and manufacturing-ready drawings for prototypes and production parts.\n\n"
            f"{website_text}"
            f"If you need CAD support for design changes, prototype development, or product documentation, I would be happy to discuss.\n\n"
            f"Best regards,\nHimanshu Rangari"
        )

    return (
        f"Hello,\n\n"
        f"I came across {company} in {city} and wanted to introduce my CAD drafting and design support services.\n\n"
        f"I help businesses with technical drawings, design support, drafting documentation, and production-ready CAD output.\n\n"
        f"{website_text}"
        f"If you have any design or drawing-related requirements, I would be glad to assist.\n\n"
        f"Best regards,\nHimanshu Rangari"
    )


def load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [dict(row) for row in reader]


def generate_leads(rows: List[Dict[str, str]]) -> List[Lead]:
    leads: List[Lead] = []
    for row in rows:
        lead = Lead(
            company_name=normalize(row.get('company_name', '')),
            industry=normalize(row.get('industry', '')),
            city=normalize(row.get('city', '')),
            phone=normalize(row.get('phone', '')),
            email=normalize(row.get('email', '')),
            website=normalize(row.get('website', '')),
            notes=normalize(row.get('notes', '')),
        )
        lead.lead_score = score_lead(row)
        lead.lead_type = detect_lead_type(row)
        lead.message = build_message(row)
        lead.whatsapp_link = build_whatsapp_link(lead.phone, lead.message)
        if lead.lead_score >= 40:
            lead.status = 'qualified'
        leads.append(lead)
    return leads


def build_whatsapp_link(phone: str, message: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if not digits:
        return ""
    return f"https://wa.me/{digits}?text={quote_plus(message)}"


def write_output(path: str, leads: List[Lead]) -> None:
    fieldnames = [
        'company_name', 'industry', 'city', 'phone', 'email', 'website', 'notes',
        'lead_score', 'lead_type', 'status', 'message', 'whatsapp_link'
    ]
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            row = asdict(lead)
            row.pop('whatsapp_link', None)
            writer.writerow({
                'company_name': lead.company_name,
                'industry': lead.industry,
                'city': lead.city,
                'phone': lead.phone,
                'email': lead.email,
                'website': lead.website,
                'notes': lead.notes,
                'lead_score': lead.lead_score,
                'lead_type': lead.lead_type,
                'status': lead.status,
                'message': lead.message,
                'whatsapp_link': lead.whatsapp_link,
            })


def send_email(recipient: str, subject: str, body: str) -> None:
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    username = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    sender = os.getenv('SENDER_EMAIL')

    if not all([host, username, password, sender]):
        raise RuntimeError('SMTP environment variables are not configured.')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)


def send_bulk_emails(leads: List[Lead], dry_run: bool = True) -> None:
    for lead in leads:
        if lead.status != 'qualified':
            continue
        if not lead.email:
            continue
        if dry_run:
            print(f"DRY RUN: would send email to {lead.email} for {lead.company_name}")
            continue
        try:
            subject = f"{os.getenv('EMAIL_SUBJECT_PREFIX', 'CAD Design Support')} - {lead.company_name}"
            send_email(lead.email, subject, lead.message)
            lead.status = 'emailed'
            print(f"Sent email to {lead.email}")
        except Exception as exc:
            print(f"Failed to email {lead.email}: {exc}")


def main():
    parser = argparse.ArgumentParser(description='CAD lead generation assistant')
    parser.add_argument('--input', required=True, help='Input CSV file with leads')
    parser.add_argument('--output', default='approved_leads.csv', help='Output CSV file')
    parser.add_argument('--send-email', action='store_true', help='Send approved emails using SMTP')
    args = parser.parse_args()

    rows = load_csv(args.input)
    leads = generate_leads(rows)
    write_output(args.output, leads)

    qualified = [lead for lead in leads if lead.status == 'qualified']
    print(f"Loaded {len(rows)} leads; {len(qualified)} qualified for outreach.")
    print(f"Output generated: {args.output}")

    if args.send_email:
        send_bulk_emails(leads, dry_run=False)
        write_output(args.output, leads)


if __name__ == '__main__':
    main()
