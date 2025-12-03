# extractor.py
from tree_sitter_languages import get_parser

LANGUAGE_MAP = {
    "py": "python",
    "js": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "tsx",
    "go": "go",
    "java": "java",
}

FUNCTION_NODES = {
    "python": ["function_definition"],
    "javascript": ["function_declaration", "method_definition"],
    "typescript": ["function_declaration", "method_definition"],
    "tsx": ["function_declaration", "method_definition"],
    "go": ["function_declaration"],
    "java": ["method_declaration"],
}


def get_language_parser(ext: str):
    lang = LANGUAGE_MAP.get(ext.lower())
    if not lang:
        return None
    return get_parser(lang)


def extract_functions(code: str, parser, ext: str):
    if parser is None:
        return []

    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node
    lang = LANGUAGE_MAP.get(ext.lower(), "")

    wanted = FUNCTION_NODES.get(lang, [])
    results = []

    def walk(node):
        if node.type in wanted:
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1
            snippet = code[node.start_byte: node.end_byte]
            results.append({
                "start": start,
                "end": end,
                "code": snippet,
                "type": node.type,
            })
        for child in node.children:
            walk(child)

    walk(root)
    return results


repo_metadata = {
    "name": "demo-repo",
    "branch": "main",
    "files": [
        {
            "path": "backend/app/main.py",
            "content": """
def add(a, b):
    return a - b  # bug

def greet(name):
    return f"Hello {name}"

class Math:
    def multiply(self, x, y):
        return x * y
"""
        },
        {
            "path": "frontend/src/utils/math.js",
            "content": """
function subtract(a, b) {
    return a - b;
}

class Calc {
    methodA(x) {
        return x * 10;
    }
}
"""
        },
        {
            "path": "frontend/src/helpers/math.ts",
            "content": """
export function add(a: number, b: number): number {
    return a + b;
}

class Service {
    compute(x: number, y: number) {
        return x - y;
    }
}
"""
        },
        {
            "path": "worker/main.go",
            "content": """
package main

func Add(a int, b int) int {
    return a - b
}

func main() {
    println(Add(2, 3))
}
"""
        },
        {
            "path": "src/com/example/App.java",
            "content": """
public class App {
    public int add(int a, int b) {
        return a - b;
    }

    private void log(String msg) {
        System.out.println(msg);
    }
}
"""
        }
    ]
}













# # test_myfile.py


# file_path = r"C:\Users\Sai\Documents\GitHub\ShipSafe\backend\myfile.py"

# # Read file contents
# with open(file_path, "r", encoding="utf8") as f:
#     code = f.read()

# ext = file_path.split(".")[-1]
# parser = get_language_parser(ext)

# if parser is None:
#     print(f"No parser for extension: {ext}")
#     exit()

# funcs = extract_functions(code, parser, ext)

# print(f"Found {len(funcs)} functions in {file_path}:")
# print("=========================================")

# for fn in funcs:
#     print(f"- {fn['type']} (lines {fn['start']}–{fn['end']})")
#     print(fn["code"])
#     print("-----------------------------------------")
