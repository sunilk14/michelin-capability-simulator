"""Pure functions for the classroom exercise (no Streamlit dependency)."""
CAPABILITIES = {
    'Data infrastructure': 'Reliable collection, integration and storage of tyre data',
    'Analytics and AI': 'Prediction of failures and prioritisation of interventions',
    'Customer IT integration': 'Connecting alerts to customers’ fleet systems',
    'Service operations': 'Technicians, processes and response to alerts',
    'People and skills': 'Cross-functional IoT, data and service expertise',
    'Sales transformation': 'Selling uptime and performance instead of tyres',
    'Partner ecosystem': 'Working with workshops and service partners',
    'Governance and incentives': 'Accountability, data rights and outcome incentives',
}
BUDGET = 100
MINIMUM = 15
TECHNICAL = list(CAPABILITIES)[:5]
COMMERCIAL = list(CAPABILITIES)[5:]


def validate_allocation(allocation):
    if set(allocation) != set(CAPABILITIES):
        return False, 'All eight capabilities must be included.'
    if any(type(v) is not int or v < 0 or v > 50 or v % 5 != 0 for v in allocation.values()):
        return False, 'Each allocation must be 0–50 in increments of 5.'
    total = sum(allocation.values())
    if total != BUDGET:
        return False, f'Allocate exactly {BUDGET} points (currently {total}).'
    return True, 'Valid allocation.'


def calculate_outcomes(a):
    """Transparent, deliberately illustrative classroom rules, not Michelin data."""
    ready = sum(v >= MINIMUM for v in a.values())
    # Bottlenecks make complementarity visible; these are teaching scores, not profits.
    prediction = min(a['Data infrastructure'], a['Analytics and AI'], a['People and skills'])
    intervention = min(prediction, a['Customer IT integration'], a['Service operations'])
    monetisation = min(intervention, a['Sales transformation'], a['Partner ecosystem'], a['Governance and incentives'])
    return {
        'Ready capabilities': ready,
        'Predictive insight': prediction,
        'Actionable service': intervention,
        'Commercial readiness': monetisation,
    }
