
import json
import sys

def main(json_args):
    args = json.loads(json_args)
    print("Received arguments:", args)
    print("1")
    print("1")
    print("1")
    print("1")
    
if __name__ == "__main__":
    json_args = sys.argv[1]
    main(json_args)