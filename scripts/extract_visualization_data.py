#!/usr/bin/env python3
"""
Extract structured visualization data from markdown evidence files.
Outputs JSON for timeline events, network graphs, and financial flows.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def extract_timeline_events(markdown_content: str) -> List[Dict[str, Any]]:
    """Extract timeline events from markdown content."""
    events = []
    
    # Pattern to match date lines and following content
    date_pattern = r'- \*\*(\d{4})\*\*[:\s]*(.+?)(?=\n-|\n\n|$)'
    date_pattern_alt = r'- \*\*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*\*[:\s]*(.+?)(?=\n-|\n\n|$)'
    date_pattern_specific = r'- \*\*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*\*[:\s]*(.+?)(?=\n-|\n\n|$)'
    
    # Extract dates with descriptions
    for match in re.finditer(date_pattern, markdown_content, re.MULTILINE | re.DOTALL):
        year = match.group(1)
        description = match.group(2).strip()
        events.append({
            "date": f"{year}-01-01",  # Default to Jan 1 if only year
            "year": int(year),
            "title": description[:100],
            "description": description,
            "category": categorize_event(description),
            "source_document": "Pre_Pandemic_Connections_The_Platform.md"
        })
    
    # Extract specific dates
    specific_date_pattern = r'- \*\*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*\*[:\s]*(.+?)(?=\n-|\n\n|$)'
    month_map = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    
    for match in re.finditer(specific_date_pattern, markdown_content, re.MULTILINE | re.DOTALL):
        date_str = match.group(1)
        description = match.group(2).strip()
        
        # Parse date
        parts = date_str.split()
        month = month_map.get(parts[0], '01')
        day = parts[1].rstrip(',').zfill(2)
        year = parts[2]
        
        events.append({
            "date": f"{year}-{month}-{day}",
            "title": description[:100],
            "description": description,
            "category": categorize_event(description),
            "source_document": "Pre_Pandemic_Connections_The_Platform.md"
        })
    
    # Sort by date
    events.sort(key=lambda x: x['date'])
    return events

def categorize_event(description: str) -> str:
    """Categorize event based on keywords."""
    desc_lower = description.lower()
    
    if any(keyword in desc_lower for keyword in ['funding', 'award', 'grant', '$', 'million', 'billion']):
        return 'funding'
    elif any(keyword in desc_lower for keyword in ['patent', 'license', 'sublicense']):
        return 'patent'
    elif any(keyword in desc_lower for keyword in ['simulation', 'exercise', 'event']):
        return 'simulation'
    elif any(keyword in desc_lower for keyword in ['agreement', 'signed', 'transfer']):
        return 'agreement'
    elif any(keyword in desc_lower for keyword in ['prediction', 'speech', 'quote']):
        return 'prediction'
    else:
        return 'general'

def extract_network_nodes(markdown_content: str) -> List[Dict[str, Any]]:
    """Extract entities for network graph."""
    entities = set()
    
    # Common entity patterns
    entity_patterns = [
        r'(Moderna|BioNTech|Pfizer|DARPA|NIH|NIAID|Gates Foundation|Bill & Melinda Gates Foundation)',
        r'(University of Pennsylvania|Penn|UNC|University of British Columbia|UBC)',
        r'(Cellscript|mRNA RiboTherapeutics|Acuitas|Arbutus|Tekmira|Inex)',
        r'(Ralph Baric|Katalin Karikó|Drew Weissman|Pieter Cullis|Thomas Madden)',
        r'(Anthony Fauci|Barney Graham|Amy Petrik)',
        r'(Johns Hopkins|WEF|World Economic Forum|CEPI)',
    ]
    
    for pattern in entity_patterns:
        matches = re.findall(pattern, markdown_content, re.IGNORECASE)
        for match in matches:
            entities.add(match)
    
    nodes = []
    for entity in sorted(entities):
        node_type = classify_entity(entity)
        nodes.append({
            "id": entity.lower().replace(' ', '_').replace('&', 'and'),
            "name": entity,
            "type": node_type,
            "influence_score": calculate_influence_score(entity, node_type)
        })
    
    return nodes

def classify_entity(entity: str) -> str:
    """Classify entity type."""
    entity_lower = entity.lower()
    
    if any(company in entity_lower for company in ['moderna', 'biontech', 'pfizer', 'cellscript', 'acuitas', 'arbutus', 'tekmira', 'inex']):
        return 'pharma'
    elif any(gov in entity_lower for gov in ['darpa', 'nih', 'niaid', 'johns hopkins', 'unc', 'penn', 'ubc']):
        return 'government'
    elif entity_lower in ['gates foundation', 'bill & melinda gates foundation', 'wef', 'world economic forum', 'cepi']:
        return 'foundation'
    elif any(person in entity_lower for person in ['ralph baric', 'katalin karikó', 'drew weissman', 'pieter cullis', 'thomas madden', 'anthony fauci', 'barney graham', 'amy petrik']):
        return 'person'
    else:
        return 'organization'

def calculate_influence_score(entity: str, entity_type: str) -> int:
    """Calculate influence score based on entity type and mentions."""
    base_scores = {
        'pharma': 85,
        'government': 75,
        'foundation': 70,
        'person': 60,
        'organization': 50
    }
    return base_scores.get(entity_type, 50)

def extract_financial_flows(markdown_content: str) -> List[Dict[str, Any]]:
    """Extract financial flow data."""
    flows = []
    
    # Pattern for money amounts
    money_pattern = r'\$?([\d.]+)\s*(million|billion|M|B)'
    
    # Find sentences with money
    lines = markdown_content.split('\n')
    for i, line in enumerate(lines):
        matches = re.finditer(money_pattern, line, re.IGNORECASE)
        for match in matches:
            amount = float(match.group(1))
            unit = match.group(2).lower()
            
            if unit in ['billion', 'b']:
                amount *= 1000  # Convert to millions
            
            # Try to identify source and target from context
            context = line.strip()
            source = extract_source_from_context(context)
            target = extract_target_from_context(context)
            
            if source and target:
                flows.append({
                    "source": source,
                    "target": target,
                    "amount": amount,  # in millions
                    "amount_display": f"${match.group(1)} {unit}",
                    "category": "funding",
                    "description": context[:200],
                    "source_document": "Pre_Pandemic_Connections_The_Platform.md"
                })
    
    return flows

def extract_source_from_context(context: str) -> str:
    """Extract source entity from context."""
    sources = ['DARPA', 'Gates Foundation', 'NIH', 'NIAID', 'Penn', 'Canadian taxpayers']
    for source in sources:
        if source.lower() in context.lower():
            return source
    return None

def extract_target_from_context(context: str) -> str:
    """Extract target entity from context."""
    targets = ['Moderna', 'BioNTech', 'Pfizer', 'Cellscript', 'Acuitas']
    for target in targets:
        if target.lower() in context.lower():
            return target
    return None

def extract_lobbying_meetings(markdown_content: str) -> List[Dict[str, Any]]:
    """Extract lobbying meeting data."""
    meetings = []
    
    # Pattern for meeting lines
    meeting_pattern = r'- \*\*([A-Za-z]+\s+\d{1,2},\s+\d{4}):\*\*\s*(.+?)(?=\n-|\n\n|$)'
    
    month_map = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    
    for match in re.finditer(meeting_pattern, markdown_content, re.MULTILINE | re.DOTALL):
        date_str = match.group(1)
        description = match.group(2).strip()
        
        # Parse date
        parts = date_str.split()
        month = month_map.get(parts[0], '01')
        day = parts[1].rstrip(',').zfill(2)
        year = parts[2]
        
        # Extract attendees and subject
        attendees = extract_attendees(description)
        subject = extract_subject(description)
        
        meetings.append({
            "date": f"{year}-{month}-{day}",
            "attendees": attendees,
            "subject": subject,
            "description": description,
            "lobbying_organization": "Innovative Medicines Canada",
            "source_document": "LOBBYING_MEETINGS_ANALYSIS.md"
        })
    
    # Sort by date
    meetings.sort(key=lambda x: x['date'])
    return meetings

def extract_attendees(description: str) -> List[str]:
    """Extract attendee names from description."""
    attendees = []
    
    # Pattern for names (Title Name)
    name_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
    matches = re.findall(name_pattern, description)
    
    for match in matches:
        if match not in ['Health', 'Industry', 'Trade', 'Science', 'Technology']:
            attendees.append(match)
    
    return attendees

def extract_subject(description: str) -> str:
    """Extract subject matter from description."""
    subjects = []
    keywords = ['Health', 'Industry', 'IP', 'Trade', 'S&T', 'Science and Technology']
    
    for keyword in keywords:
        if keyword in description:
            subjects.append(keyword)
    
    return ', '.join(subjects) if subjects else 'General'

def main():
    """Main extraction function."""
    evidence_dir = Path('/home/x99/Desktop/FUCK/EVIDENCE_COLLECTED')
    output_dir = Path('/home/x99/Desktop/FUCK/frontend/src/data')
    output_dir.mkdir(exist_ok=True)
    
    # Read the main platform evidence file
    platform_file = evidence_dir / 'Pre_Pandemic_Connections_The_Platform.md'
    with open(platform_file, 'r') as f:
        content = f.read()
    
    # Read lobbying meetings file
    lobbying_file = evidence_dir / 'LOBBYING_MEETINGS_ANALYSIS.md'
    with open(lobbying_file, 'r') as f:
        lobbying_content = f.read()
    
    # Extract data
    timeline_events = extract_timeline_events(content)
    network_nodes = extract_network_nodes(content)
    financial_flows = extract_financial_flows(content)
    lobbying_meetings = extract_lobbying_meetings(lobbying_content)
    
    # Create output data structure
    visualization_data = {
        "timeline_events": timeline_events,
        "network_nodes": network_nodes,
        "financial_flows": financial_flows,
        "lobbying_meetings": lobbying_meetings,
        "metadata": {
            "extracted_at": datetime.now().isoformat(),
            "source_files": [str(platform_file), str(lobbying_file)],
            "total_events": len(timeline_events),
            "total_nodes": len(network_nodes),
            "total_flows": len(financial_flows),
            "total_meetings": len(lobbying_meetings)
        }
    }
    
    # Write to JSON
    output_file = output_dir / 'visualization_data.json'
    with open(output_file, 'w') as f:
        json.dump(visualization_data, f, indent=2)
    
    print(f"✅ Extracted {len(timeline_events)} timeline events")
    print(f"✅ Extracted {len(network_nodes)} network nodes")
    print(f"✅ Extracted {len(financial_flows)} financial flows")
    print(f"✅ Extracted {len(lobbying_meetings)} lobbying meetings")
    print(f"✅ Saved to {output_file}")
    
    # Also write individual files for easier consumption
    with open(output_dir / 'timeline_events.json', 'w') as f:
        json.dump(timeline_events, f, indent=2)
    
    with open(output_dir / 'network_nodes.json', 'w') as f:
        json.dump(network_nodes, f, indent=2)
    
    with open(output_dir / 'financial_flows.json', 'w') as f:
        json.dump(financial_flows, f, indent=2)
    
    with open(output_dir / 'lobbying_meetings.json', 'w') as f:
        json.dump(lobbying_meetings, f, indent=2)
    
    print("✅ Individual data files saved")

if __name__ == '__main__':
    main()
