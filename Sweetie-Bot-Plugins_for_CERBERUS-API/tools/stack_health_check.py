import json, pathlib

def main():
    endpoints = json.loads(pathlib.Path("stack/configs/plugin-endpoints.json").read_text(encoding="utf-8"))
    print("Configured endpoints:")
    for name, url in endpoints.items():
        print(f"- {name}: {url}")
    print("\nLive HTTP probing should be added when running inside the target deployment environment.")

if __name__ == "__main__":
    main()
