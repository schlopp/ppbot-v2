import discord
import uuid
import typing


class Component():
    """
    Component. MM. Sexy. Delicious.
    """


class ActionRow(Component):
    """
    ActionRow
    """

    def __init__(self, *components:typing.List[Component]):
        self.type = 1
        self.components = components
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "components": [i.to_dict() for i in self.components],
        }


class Button(Component):
    """
    Create button. So sexy.
    """

    def __init__(
                self, label:str, *, style:int=1,
                disabled:bool=False, custom_id:str="",
                emoji:str="", url:str=""):
        self.label = label
        self.style = style
        self.disabled = disabled
        self.custom_id = custom_id or str(uuid.uuid1())
        self.emoji = emoji or None
        self.url = url or None
    
    def to_dict(self) -> dict:
        payload = {
            "type": 2,
            "style": self.style,
            "label": self.label,
            "disabled": self.disabled,
            "custom_id": self.custom_id,
            "emoji": self.emoji,
            "url": self.url,
        }

        if self.style == 5:
            payload.pop("custom_id")
        else:
            payload.pop("url")

        return payload

def send_message(
                self, channel_id, content,
                *, tts=False, embed=None, nonce=None,
                allowed_mentions=None,
                message_reference=None, components=None):
        """
        ME WHEN MESSAGE IS SENDING
        """
        r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
        payload = {}

        if content:           payload['content'] = content
        if tts:               payload['tts'] = True
        if embed:             payload['embed'] = embed
        if nonce:             payload['nonce'] = nonce
        if allowed_mentions:  payload['allowed_mentions'] = allowed_mentions
        if message_reference: payload['message_reference'] = message_reference
        if components:        payload['components'] = components

        return self.request(r, json=payload)

def send_multipart_helper(
        self,
        route,
        *,
        files,
        content=None,
        tts=False,
        embed=None,
        embeds=None,
        nonce=None,
        allowed_mentions=None,
        message_reference=None,
        components=None,
    ):
        form = []

        payload = {'tts': tts}
        if content:             payload['content'] = content
        if embed:               payload['embed'] = embed
        if embeds:              payload['embeds'] = embeds
        if nonce:               payload['nonce'] = nonce
        if allowed_mentions:    payload['allowed_mentions'] = allowed_mentions
        if message_reference:   payload['message_reference'] = message_reference
        if components:          payload['components'] = components

        form.append({'name': 'payload_json', 'value': discord.utils.to_json(payload)})
        if len(files) == 1:
            file = files[0]
            form.append(
                {
                    'name': 'file',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
        else:
            for index, file in enumerate(files):
                form.append(
                    {
                        'name': f'file{index}',
                        'value': file.fp,
                        'filename': file.filename,
                        'content_type': 'application/octet-stream',
                    }
                )

        return self.request(route, form=form, files=files)

def send_files(
                self, channel_id, *, files, content=None,
                tts=False, embed=None, nonce=None,
                allowed_mentions=None, message_reference=None,
                components=None):
        """
        ME WHEN FILES???? MAYBE ALSO CONTENT
        """
        r = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
        return self.send_multipart_helper(
            r, files=files, content=content,
            tts=tts, embed=embed, nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=components,
        )

discord.http.HTTPClient.send_message = send_message
discord.http.HTTPClient.send_multipart_helper = send_multipart_helper
discord.http.HTTPClient.send_files = send_files

async def send(
            self, content=None, *, tts=False,
            embed=None, file=None, files=None,
            delete_after=None, nonce=None,
            allowed_mentions=None, reference=None,
            mention_author=None, components=None):
        """
        |coro|
        Sends a message to the destination with the content given.
        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.
        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~discord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~discord.File` objects.
        **Specifying both parameters will lead to an exception**.
        If the ``embed`` parameter is provided, it must be of type :class:`~discord.Embed` and
        it must be a rich embed type.
        Parameters
        ------------
        content: :class:`str`
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.
            .. versionadded:: 1.4
        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`]
            A reference to the :class:`~discord.Message` to which you are replying, this can be created using
            :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.
            .. versionadded:: 1.6
        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.
            .. versionadded:: 1.6
        components: Optional[:class:`bool`]
        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or the ``reference`` object is not a :class:`~discord.Message`
            or :class:`~discord.MessageReference`.
        Returns
        ---------
        :class:`~discord.Message`
            The message that was sent.
        """

        channel = await self._get_channel()
        state = self._state
        content = str(content) if content is not None else None
        if embed is not None:
            embed = embed.to_dict()

        if allowed_mentions is not None:
            if state.allowed_mentions is not None:
                allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()

        if mention_author is not None:
            allowed_mentions = allowed_mentions or discord.AllowedMentions().to_dict()
            allowed_mentions['replied_user'] = bool(mention_author)

        if reference is not None:
            try:
                reference = reference.to_message_reference_dict()
            except AttributeError:
                raise discord.InvalidArgument('reference parameter must be Message or MessageReference') from None

        if components is not None:
            components = [i.to_dict() for i in components]

        if file is not None and files is not None:
            raise discord.InvalidArgument('cannot pass both file and files parameter to send()')

        if file is not None:
            if not isinstance(file, discord.File):
                raise discord.InvalidArgument('file parameter must be File')

            try:
                data = await state.http.send_files(
                    channel.id, files=[file], allowed_mentions=allowed_mentions,
                    content=content, tts=tts, embed=embed, nonce=nonce,
                    message_reference=reference, components=components
                )
            finally:
                file.close()

        elif files is not None:
            if len(files) > 10:
                raise discord.InvalidArgument('files parameter must be a list of up to 10 elements')
            elif not all(isinstance(file, discord.File) for file in files):
                raise discord.InvalidArgument('files parameter must be a list of File')

            try:
                data = await state.http.send_files(
                    channel.id, files=files, content=content, tts=tts,
                    embed=embed, nonce=nonce, allowed_mentions=allowed_mentions,
                    message_reference=reference, components=components
                )
            finally:
                for f in files:
                    f.close()
        else:
            data = await state.http.send_message(
                channel.id, content, tts=tts, embed=embed,
                nonce=nonce, allowed_mentions=allowed_mentions,
                message_reference=reference, components=components
            )

        ret = state.create_message(channel=channel, data=data)
        if delete_after is not None:
            await ret.delete(delay=delete_after)
        return ret

discord.abc.Messageable.send = send