import unittest

from persian_eval.backends import (
    extract_anthropic_text,
    extract_response_text,
    normalize_anthropic_messages_url,
)


class BackendsTests(unittest.TestCase):
    def test_extract_response_text_from_output_text(self):
        self.assertEqual(extract_response_text({"output_text": " پاسخ "}), "پاسخ")

    def test_extract_response_text_from_output_content(self):
        data = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "الف"},
                        {"type": "output_text", "text": "ب"},
                    ]
                }
            ]
        }
        self.assertEqual(extract_response_text(data), "الف\nب")

    def test_extract_anthropic_text_ignores_thinking_blocks(self):
        data = {
            "content": [
                {"type": "thinking", "thinking": "hidden"},
                {"type": "text", "text": " الف "},
                {"type": "text", "text": "توضیح"},
            ]
        }
        self.assertEqual(extract_anthropic_text(data), "الف\nتوضیح")

    def test_normalize_anthropic_messages_url(self):
        self.assertEqual(
            normalize_anthropic_messages_url("https://api.anthropic.com"),
            "https://api.anthropic.com/v1/messages",
        )
        self.assertEqual(
            normalize_anthropic_messages_url("https://api.anthropic.com/v1"),
            "https://api.anthropic.com/v1/messages",
        )
        self.assertEqual(
            normalize_anthropic_messages_url("https://api.anthropic.com/v1/messages"),
            "https://api.anthropic.com/v1/messages",
        )


if __name__ == "__main__":
    unittest.main()
