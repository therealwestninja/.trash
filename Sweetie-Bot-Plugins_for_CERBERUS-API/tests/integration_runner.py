import json, pathlib

def main():
    contract = json.loads(pathlib.Path("tests/contract_matrix.json").read_text(encoding="utf-8"))
    print("Sweetie Integration Runner")
    print("=========================")
    for service in contract["services"]:
        print(f"service: {service}")
        for route in contract["required_contracts"]:
            print(f"  expects: {route}")
    print("\nNext step: replace with live HTTP probing + scenario assertions.")

if __name__ == "__main__":
    main()
