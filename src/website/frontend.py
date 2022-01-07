import os
import typing

from aiohttp import web
from aiohttp.web import Request, Response, RouteTableDef
from aiohttp_jinja2 import template
from discord.ext import vbu  # type: ignore

routes = RouteTableDef()


@routes.get("/")
async def index(request: Request) -> Response:
    return web.HTTPPermanentRedirect("/commands")


@routes.get("/commands")
@template("commands.html.j2")
async def commands(request: Request):
    """
    Handles the commands documentation page for the bot.
    """

    bot: vbu.Bot = request.app["bots"]["bot"]

    # Some type annotations
    class _CommandPayload(typing.TypedDict):
        name: str
        help: typing.Optional[str]
        signature: typing.Optional[str]
        fields: typing.List[typing.Dict[str, typing.Any]]

    class _Payload(typing.TypedDict):
        commands: typing.List[_CommandPayload]
        css: typing.List[str]

    payload: _Payload = {
        "commands": [],
        "css": [
            f"commands.css?v={os.path.getmtime('website/static/css/commands.css')}"
        ],
    }

    for command in bot.commands:
        if any([check.__qualname__.startswith("is_owner") for check in command.checks]):
            continue

        command_payload: _CommandPayload = {
            "name": command.name,
            "help": command.help,
            "signature": command.signature,
            "fields": [],
        }

        if command.param_descriptions:
            command_payload["fields"].append(
                {
                    "name": "Help",
                    "value": command.param_descriptions,
                    "type": command.param_descriptions.__class__.__name__,
                }
            )
        if command.full_parent_name:
            command_payload["fields"].append(
                {
                    "name": "Parent",
                    "value": command.full_parent_name,
                    "type": command.full_parent_name.__class__.__name__,
                }
            )

        payload["commands"].append(command_payload)
    return payload


@routes.get("/schlopp")
@template("schlopp.html")
async def schlopp(request: Request):
    """
    Handles the schlopp page.
    """

    return {}
