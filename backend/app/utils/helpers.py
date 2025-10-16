def is_error_response(response_text: str) -> bool:
    if not response_text:
        return True

    # Pola umum error dari sistem
    error_indicators = [
        "I apologize, but I encountered an error",
        "An error occurred while generating",
        "I’m sorry, something went wrong",
        "Error generating a response",
    ]

    return any(indicator.lower() in response_text.lower() for indicator in error_indicators)
