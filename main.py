import asyncio

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


vkToken = ''
# Сюда вставляешь свой токен (Я юзал от кейта. Получить можно тут https://vkhost.github.io )


myId =  # Здесь вводишь свой айди (прим. myId = 1)

triggerWord = '' # Триггер слово в кавычках, с маленькой буквы для удаления сообщений


vk_session = vk_api.VkApi(token=vkToken)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

pastSafe = None
argNumber = None
toDelete = []


async def msgDelete():
    try:
        vk.messages.delete(message_ids=str(toDelete),
                           delete_for_all=1)
    except vk_api.exceptions.ApiError:
        vk.messages.delete(message_ids=str(toDelete), delete_for_all=0)
    toDelete.clear()


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.text.lower().startswith(triggerWord) and event.from_me and len(
            event.text.split()) is 1:
        if len(event.text) > len(
                triggerWord):
            if event.text[len(triggerWord):] is '1':
                argNumber = 2
            else:
                if event.text[len(triggerWord):].isdigit() is True:
                    argNumber = int(event.text[len(
                        triggerWord):]) + 1
        else:
            argNumber = 2
            pastSafe = True
        if event.text[len(triggerWord):].isdigit() is True or pastSafe is True:
            for n in vk.messages.getHistory(peer_id=event.peer_id).get('items'):
                if n['from_id'] == myId and len(toDelete) < argNumber:
                    toDelete.append(n['id'])
            toDelete.append(event.message_id)
            pastSafe = None
            asyncio.run(msgDelete())