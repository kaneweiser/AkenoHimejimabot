#    This file is part of NiceGrill.

#    NiceGrill is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    NiceGrill is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with NiceGrill.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
from urllib import request
from AkenoHimejimabot import utils

class Renamer:
@run_async
def rename(message):
    reply = await message.get_reply_message()
    name = utils.get_arg(message)
    if not message.is_reply or not reply.media:
       await message.edit("<i>Reply to a message with media</i>")
       return
    await message.edit("<i>Downloading..</i>")
       dl = await reply.download_media()
       if not name:
          name = dl
    await message.edit("<i>Renaming..</i>")
       file = await message.client.upload_file(dl)
       file.name = name
       await message.client.send_file(
          message.chat_id, file=file, reply_to=reply.id)
       await message.delete()
       os.remove(dl)

RNAME_HANDLER = CommandHandler('rename', rename)
dispatcher.add_handler(RNAME_HANDLER)
__mod_name__ = "rename"
__command_list__ = ['rename']
__handlers__ = [RNAME_HANDLER]
