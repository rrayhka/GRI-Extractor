from typing import Dict, List, Tuple, Optional, Any
GRI_Dicts = {
    "GRI 2: General Disclosures 2021": {
        "2-1": "Organizational details",
        "2-2": "Entities included in the organization’s sustainability reporting",
        "2-3": "Reporting period, frequency and contact point",
        "2-4": "Restatements of information",
        "2-5": "External assurance",
        "2-6": "Activities, value chain and other business relationships",
        "2-7": "Employees",
        "2-8": "Workers who are not employees",
        "2-9": "Governance structure and composition",
        "2-10": "Nomination and selection of the highest governance body",
        "2-11": "Chair of the highest governance body",
        "2-12": "Role of the highest governance body in overseeing the management of impacts",
        "2-13": "Delegating authority for managing impacts",
        "2-14": "Role of the highest governance body in sustainability reporting",
        "2-15": "Conflicts of interest",
        "2-16": "Communication of critical concerns",
        "2-17": "Collective knowledge of the highest governance body",
        "2-18": "Evaluation of the performance of the highest governance body",
        "2-19": "Remuneration policies",
        "2-20": "Process to determine remuneration",
        "2-21": "Annual total compensation ratio",
        "2-22": "Statement on sustainable development strategy",
        "2-23": "Policy commitments",
        "2-24": "Embedding policy commitments",
        "2-25": "Processes to remediate negative impacts",
        "2-26": "Mechanisms for seeking advice and raising concerns",
        "2-27": "Compliance with laws and regulations",
        "2-28": "Membership associations",
        "2-29": "Approach to stakeholder engagement",
        "2-30": "Collective bargaining agreements"
    },
    "GRI 3: Material Topics 2021": {
        "3-1": "Process to determine material topics",
        "3-2": "List of material topics",
        "3-3": "Management of material topics"
    },
    "GRI 101: Biodiversity 2024": {
        "101-1": "Policies to halt and reverse biodiversity loss",
        "101-2": "Management of biodiversity impacts",
        "101-3": "Access and benefit-sharing",
        "101-4": "Identification of biodiversity impacts",
        "101-5": "Locations with biodiversity impacts",
        "101-6": "Direct drivers of biodiversity loss",
        "101-7": "Changes to the state of biodiversity",
        "101-8": "Ecosystem services"
    },
    "GRI 201: Economic Performance 2016": {
        "201-1": "Direct economic value generated and distributed",
        "201-2": "Financial implications and other risks and opportunities due to climate change",
        "201-3": "Defined benefit plan obligations and other retirement plans",
        "201-4": "Financial assistance received from government"
    },
    "GRI 202: Market Presence 2016": {
        "202-1": "Ratios of standard entry level wage by gender compared to local minimum wage",
        "202-2": "Proportion of senior management hired from the local community"
    },
    "GRI 203: Indirect Economic Impacts 2016": {
        "203-1": "Infrastructure investments and services supported",
        "203-2": "Significant indirect economic impacts"
    }, 
    "GRI 204: Procurement Practices 2016": {
        "204-1": "Proportion of spending on local suppliers"
    },
    "GRI 205: Anti-Corruption 2016": {
        "205-1": "Operations assessed for risks related to corruption",
        "205-2": "Communication and training about anti-corruption policies and procedures",
        "205-3": "Confirmed incidents of corruption and actions taken"
    },
    "GRI 206: Anti-Competitive Behavior 2016": {
        "206-1": "Legal actions for anti-competitive behavior, anti-trust, and monopoly practices"
    },
    "GRI 207: Tax 2019": {
        "207-1": "Approach to tax",
        "207-2": "Tax governance, control, and risk management",
        "207-3": "Stakeholder engagement and management of concerns related to tax",
        "207-4": "Country-by-country reporting"
    },
    "GRI 301: Materials 2016": {
        "301-1": "Materials used by weight or volume",
        "301-2": "Recycled input materials used",
        "301-3": "Reclaimed products and their packaging materials"
    },
    "GRI 302: Energy 2016": {
        "302-1": "Energy consumption within the organization",
        "302-2": "Energy consumption outside of the organization",
        "302-3": "Energy intensity",
        "302-4": "Reduction of energy consumption",
        "302-5": "Reduction in energy requirements of products and services"
    },
    "GRI 303: Water and Effluents 2018": {
        "303-1": "Interactions with water as a shared resource",
        "303-2": "Management of water discharge-related impacts",
        "303-3": "Water withdrawal",
        "303-4": "Water discharge",
        "303-5": "Water consumption"
    },
    "GRI 304: Biodiversity 2016": {
        "304-1": "Operational sites owned, leased, managed in, or adjacent to, protected areas and areas of high biodiversity value outside protected areas",
        "304-2": "Significant impacts of activities, products, and services on biodiversity",
        "304-3": "Habitat protection and restoration",
        "304-4": "IUCN Red List species and national conservation list species with habitats in areas affected by operations"
    },
    "GRI 305: Emissions 2016": {
        "305-1": "Direct (Scope 1) GHG emissions",
        "305-2": "Energy indirect (Scope 2) GHG emissions",
        "305-3": "Other indirect (Scope 3) GHG emissions",
        "305-4": "GHG emissions intensity",
        "305-5": "Reduction of GHG emissions",
        "305-6": "Emissions of ozone-depleting substances (ODS)",
        "305-7": "Nitrogen oxides (NOX), sulfur oxides (SOX), and other significant air emissions"  
    },
    "GRI 306: Effluents and Waste 2016": {
        "306-1": "Water discharge by quality and destination",
        "306-2": "Waste by type and disposal method",
        "306-3": "Significant spills",
        "306-4": "Transport of hazardous waste",
        "306-5": "Water bodies affected by water discharges and/or runoff"
    },
    "GRI 306: Waste 2020": {
        "306-1": "Waste generation and significant waste-related impacts",
        "306-2": "Management of significant waste-related impacts",
        "306-3": "Waste generated",
        "306-4": "Waste diverted from disposal",
        "306-5": "Waste directed to disposal"
    },
    "GRI 308: Supplier Environmental Assessment 2016": {
        "308-1": "New suppliers that were screened using environmental criteria",
        "308-2": "Negative environmental impacts in the supply chain and actions taken"
    },
    "GRI 401: Employment 2016": {
        "401-1": "New employee hires and employee turnover",
        "401-2": "Benefits provided to full-time employees that are not provided to temporary or part-time employees",
        "401-3": "Parental leave"
    },
    "GRI 402: Labor/Management Relations 2016": {
        "402-1": "Minimum notice periods regarding operational changes"
    },
    "GRI 403: Occupational Health and Safety 2018": {
        "403-1": "Occupational health and safety management system",
        "403-2": "Hazard identification, risk assessment, and incident investigation",
        "403-3": "Occupational health services",
        "403-4": "Worker participation, consultation, and communication",
        "403-5": "Worker training on occupational health and safety",
        "403-6": "Promotion of worker health",
        "403-7": "Prevention and mitigation of occupational health and safety impacts directly linked by business relationships",
        "403-8": "Workers covered by an occupational health and safety management system",
        "403-9": "Work-related injuries",
        "403-10": "Work-related ill health",
    },
    "GRI 404: Training and Education 2016": {
        "404-1": "Average hours of training per year per employee",
        "404-2": "Programs for upgrading employee skills and transition assistance programs",
        "404-3": "Percentage of employees receiving regular performance and career development reviews"
    },
    "GRI 405: Diversity and Equal Opportunity 2016": {
        "405-1": "Diversity of governance bodies and employees",
        "405-2": "Ratio of basic salary and remuneration of women to men",
        "405-3": "Parental leave"
    },
    "GRI 406: Non-discrimination 2016": {
        "406-1": "Incidents of discrimination and corrective actions taken"
    },
    "GRI 407: Freedom of Association and Collective Bargaining 2016": {
        "407-1": "Operations and suppliers in which the right to freedom of association and collective bargaining may be at risk"
    },
    "GRI 408: Child Labor 2016"	: {
        "408-1": "Operations and suppliers at significant risk for incidents of child labor"
    },
    "GRI 409: Forced or Compulsory Labor 2016": {
        "409-1": "Operations and suppliers at significant risk for incidents of forced or compulsory labor"
    },			
    "GRI 410: Security Practices 2016": {
        "410-1": "Security personnel trained in human rights policies or procedures"
    },
    "GRI 411: Rights of Indigenous Peoples 2016": {
        "411-1": "Operations and suppliers in which the rights of indigenous peoples may be at risk"
    },
    "GRI 412: Human Rights Assessment 2016": {
        "412-1": "Operations that have been subject to human rights reviews or impact assessments",
        "412-2": "Employee training on human rights policies or procedures",
        "412-3": "Significant investment agreements and contracts that include human rights clauses or that underwent human rights screening"
    },
    "GRI 413: Local Communities 2016": {
        "413-1": "Operations with local community engagement, impact assessments, and development programs",
        "413-2": "Operations with significant actual and potential negative impacts on local communities"
    },
    "GRI 414: Supplier Social Assessment 2016": {
        "414-1": "New suppliers that were screened using social criteria",
        "414-2": "Negative social impacts in the supply chain and actions taken"
    },
    "GRI 415: Public Policy 2016": {
        "415-1": "Political contributions"
    },
    "GRI 416: Customer Health and Safety 2016": {
        "416-1": "Assessment of the health and safety impacts of product and service categories",
        "416-2": "Incidents of non-compliance concerning the health and safety impacts of products and services"
    },
    "GRI 417: Marketing and Labeling 2016": {
        "417-1": "Requirements for product and service information and labeling",
        "417-2": "Incidents of non-compliance concerning product and service information and labeling",
        "417-3": "Incidents of non-compliance concerning marketing communications"
    },
    "GRI 418: Customer Privacy 2016": {
        "418-1": "Substantiated complaints concerning breaches of customer privacy and losses of customer data"
    },
}
gri_dicts = GRI_Dicts

def _create_empty_result() -> Dict[str, List[Dict[str, str]]]:
    """Create result dictionary with all GRI codes marked as 'none'."""
    results = []
    for material_topic, codes in gri_dicts.items():
        for gri_code, description in codes.items():
            results.append({
                "material_topic": material_topic,
                "gri_code": gri_code,
                "status": "none",
                "description": description,
                "disclosure": "none"
            })
    print({"gri_disclosures": results})
_create_empty_result()

# print(_create_empty_result())  # Example usage, replace None with actual instance if needed