from rest_framework.parsers import JSONParser, ParseError
import json

class CustomJSONParser(JSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', 'utf-8')

        try:
            data = stream.read().decode(encoding)
            cleaned_data = data.strip()
            if not cleaned_data:
                return {}
            return json.loads(cleaned_data)
        except ValueError:
            # Handle invalid JSON by returning empty dict for PATCH requests
            return {}