def propose_semantic_fixes(function_name: str):
    if function_name == "multiply":
        return [
            {
                "option": "Standard multiplication",
                "code": "def multiply(a, b):\n    return a * b",
                "confidence": "high"
            }
        ]

    return []
