# process buyback table from yfistats.com
"""
Vaults Aug-Oct Funding Request Budget Tracker
Issue #354: Tracks allocated vs spent budget for Vaults product funding.
"""

BUDGET_ALLOCATIONS = {
    "smart_contract_development": 135000,
    "security_monitoring": 44550,
    "business_development": 27500,
    "webops": 90216,
    "production_engineering": 45000,
}

TOTAL_BUDGET = sum(BUDGET_ALLOCATIONS.values())


def get_allocation(category: str) -> int:
    """Return the allocated budget for a given category."""
    if category not in BUDGET_ALLOCATIONS:
        raise ValueError(f"Unknown budget category: {category}")
    return BUDGET_ALLOCATIONS[category]


def validate_budget(spent: dict[str, int]) -> dict[str, dict]:
    """
    Validate spending against allocations.
    Returns a report with remaining budget and overage warnings.
    """
    report = {}
    total_spent = 0
    for category, allocation in BUDGET_ALLOCATIONS.items():
        category_spent = spent.get(category, 0)
        remaining = allocation - category_spent
        report[category] = {
            "allocated": allocation,
            "spent": category_spent,
            "remaining": remaining,
            "over_budget": remaining < 0,
        }
        total_spent += category_spent
    report["total"] = {
        "allocated": TOTAL_BUDGET,
        "spent": total_spent,
        "remaining": TOTAL_BUDGET - total_spent,
        "over_budget": (TOTAL_BUDGET - total_spent) < 0,
    }
    return report


if __name__ == "__main__":
    import json
    import sys

    # Example usage: pass spent amounts as JSON via stdin or CLI arg
    if len(sys.argv) > 1:
        spent_data = json.loads(sys.argv[1])
    else:
        spent_data = {}

    report = validate_budget(spent_data)
    print(json.dumps(report, indent=2))
import json

BUYBACK = "Ignore:Buying YFI"
FOLDER = "reports/financial/buybacks"
INPUT = f"{FOLDER}/2022-01-28-yfi-crv-buy-backs.csv"
OUPUT = f"{FOLDER}/buybacks.json"


def process():
    data = []
    with open(INPUT, "r") as csv_file:
        column_to_name = {"timestamp": 1, "yfiAmount": 6, "usdValue": -2, "tokenAmount": -3, "token": -4, "hash": 2}
        csv_reader = csv.reader(csv_file, delimiter=",")
        id = 1
        for lines in csv_reader:
            if lines[-1] == BUYBACK and lines[column_to_name["yfiAmount"]] != "":
                j = {}
                j["id"] = id
                id += 1
                for col, i in column_to_name.items():
                    try:
                        j[col] = float(lines[i].replace(",", ""))
                    except ValueError:
                        j[col] = lines[i]
                data.append(j)

    with open(OUPUT, "w") as json_file:
        json.dump(data, json_file, indent=2)


def main():
    process()
    print("Done!")
