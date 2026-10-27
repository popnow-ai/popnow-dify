from dify_plugin import Tool
from client import PopNowClient, PopNowError

class PopNowTool(Tool):
    operation = ''
    def _invoke(self, tool_parameters):
        try:
            data = PopNowClient(self.runtime.credentials.get('api_key')).invoke(self.operation, tool_parameters)
        except PopNowError as error:
            yield self.create_json_message({'error': str(error)})
            yield self.create_text_message(str(error))
            return
        yield self.create_json_message({'data': data})
