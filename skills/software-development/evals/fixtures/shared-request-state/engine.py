from dataclasses import dataclass


@dataclass
class ReportConfig:
    template: str
    request_id: str | None = None


class ReportEngine:
    def __init__(self, config, renderer):
        self.config = config
        self.renderer = renderer

    async def render(self, request_id):
        self.config.request_id = request_id
        body = await self.renderer(self.config.template)
        return {"request_id": self.config.request_id, "body": body}
