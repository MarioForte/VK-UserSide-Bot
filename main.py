import random
import threading
import time
import asyncio

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


vkToken = ''
# Сюда вставляешь свой токен (Я юзал от кейта. Получить можно тут https://vkhost.github.io )


myId =  # Здесь вводишь свой айди (прим. myId = 1)


contestTriggerList = ()  # Листик слов триггеров для уведомления о розыгрыше:
# Прим. contestTriggerList = ('розыгрыш', 'конкурс')

contestWhiteList = () # Вайтлист айди для триггеров на конкурс:
# Прим. contestWhiteList = (1, 2, 3)

startMyContestTrigger = ''  # Вводишь в кавычках команду, с которой начинается свой розыгрыш
triggerWord = '' # Триггер слово в кавычках, с маленькой буквы для удаления сообщений


vk_session = vk_api.VkApi(token=vkToken)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

pastSafe = None
argNumber = None
toDelete = []
startedContest = {}
contestPeerId = {}
contestMsgId = {}
contestForAll = {}
contestInstruction = {}
setupTimer = {}
contestList = {}
contestMemberList = {}

def msgDelete():
    try:
        vk.messages.delete(message_ids=str(toDelete),
                           delete_for_all=1)
    except vk_api.exceptions.ApiError:
        vk.messages.delete(message_ids=str(toDelete), delete_for_all=0)
    toDelete.clear()

async def contestMember(cmId):
    p = 0
    localPeerId = cmId
    for h in contestMemberList.get(localPeerId):
        n = vk.users.get(user_ids=contestMemberList.get(localPeerId)[p])[0].get(
            'first_name')
        o = '[id' + str(contestMemberList.get(localPeerId)[p]) + '|' + str(n) + ']'
        if o not in contestList.get(localPeerId):
            contestList[localPeerId].append(o)
        p = p + 1
    return contestList[localPeerId]

async def contestValidator():
    if event.peer_id == contestPeerId.get(event.text):
        return True
    else:
        return False

async def contestCleaner(ccId):
    global setupTimer, contestPeerId, startedContest, contestList, contestMemberList, contestMsgId, contestInstruction
    localPeerId = ccId
    startedContest.pop(localPeerId)
    contestMsgId.pop(localPeerId)
    contestMemberList.pop(localPeerId)
    contestList.pop(localPeerId)
    setupTimer.pop(localPeerId)
    contestInstruction.pop(localPeerId)

def contestUpdater(cuId):
    global setupTimer, startedContest
    localPeerId = cuId
    while True:
        time.sleep(60)
        setupTimer.update({localPeerId: int(setupTimer.get(localPeerId)) - 1})
        try:
            vk.messages.edit(peer_id=localPeerId, message_id=contestMsgId.get(localPeerId),
                             message='Ого! Запущено начало розыгрыша. \nДля принятия участия введите: ' +
        contestInstruction.get(localPeerId) + '\n\n До окончания розыгрыша: ' + str(
        setupTimer.get(localPeerId)) + 'мин.\n\nУчастники в розыгрыше: '
                                     +', '.join(asyncio.run(contestMember(localPeerId))))
        except IndexError:
            asyncio.run(contestCleaner(localPeerId))
        if setupTimer.get(localPeerId) == 0:
            if not asyncio.run(contestMember(localPeerId)):
                vk.messages.send(
                    peer_id=localPeerId,
                    random_id=random.randint(1, 922337203685477580),
                    message='В розыгрыше нет победителя, в связи с отсутствием участников!',
                    reply_to=contestMsgId.get(localPeerId))
                asyncio.run(contestCleaner(localPeerId))
                break
            else:
                vk.messages.send(
                    peer_id=localPeerId,
                    random_id=random.randint(1, 922337203685477580),
                    message='В розыгрыше побеждает ' + random.choice(asyncio.run(contestMember(localPeerId))) +
                            '\nПоздравляем!',
                    reply_to=contestMsgId.get(localPeerId))
                asyncio.run(contestCleaner(localPeerId))
                break


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
            msgDelete()
    if event.type == VkEventType.MESSAGE_NEW and event.from_chat and any(
            contestTriggerWord in event.text.lower() for contestTriggerWord in
            contestTriggerList):
        if event.user_id in contestWhiteList:
            vk.messages.send(
                peer_id=myId,
                random_id=random.randint(1, 922337203685477580),
                message='Потенциальное начало конкурса/розыгрыша в "' +
                        vk.messages.getChatPreview(peer_id=event.peer_id).get('preview')['title'] + '"\n\n' +
                        vk.users.get(user_ids=myId)[0].get('first_name') + ', не пропусти его, котик ♥',
                forward_messages=event.message_id)
    if event.type == VkEventType.MESSAGE_NEW and event.text.lower().startswith(
            startMyContestTrigger) and (event.from_me == True or contestForAll.get(event.peer_id) == 1) \
            and (startedContest.get(event.peer_id) is False or
                                                          startedContest.get(event.peer_id) is None):
        if len(event.text) > len(startMyContestTrigger) and event.text.split(' ')[1].isdigit() is True:
            setupTimer.update({event.peer_id: int(event.text.split(' ')[1])})
            try:
                vk.messages.delete(message_ids=event.message_id, delete_for_all=1)
            except vk_api.exceptions.ApiError:
                pass
            try:
                contestInstruction.update({event.peer_id: ' '.join(
                    event.text.split(' ')[2:len(event.text.split(' '))])})
                if not event.user_id == myId:
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=random.randint(1, 922337203685477580),
                        message='[id' + str(event.user_id) + '|@' + str(event.user_id) + '] запустил начало конкурса.')
                vk.messages.send(
                    peer_id=event.peer_id,
                    random_id=random.randint(1, 922337203685477580),
                    message='Ого! Запущено начало розыгрыша.\nДля принятия участия введите: '
                        + str(contestInstruction.get(event.peer_id)) +
                        '\n\n До окончания розыгрыша: ' + str(setupTimer.get(event.peer_id)) +
                        'мин.\n\nУчастники в розыгрыше: ')
            except IndexError:
                asyncio.run(contestCleaner(event.user_id))
    if event.type == VkEventType.MESSAGE_NEW and event.from_me and \
                        event.text.startswith('Ого!') and startedContest.get(event.peer_id) is None:
        contestPeerId.update({contestInstruction.get(event.peer_id): event.peer_id})
        contestMsgId.update({event.peer_id: event.message_id})
        contestMemberList.update({event.peer_id: []})
        contestList.update({event.peer_id: []})
        startedContest.update({event.peer_id: True})
        thread = threading.Thread(target=contestUpdater, args=(event.peer_id,))
        thread.start()
    if event.type == VkEventType.MESSAGE_NEW and event.from_chat and asyncio.run(contestValidator()) is True:
        if event.user_id not in contestMemberList.get(event.peer_id):
            contestMemberList.get(event.peer_id).append(event.user_id)
            try:
                vk.messages.edit(peer_id=event.peer_id, message_id=contestMsgId.get(event.peer_id),
                                 message='Ого! Запущено начало розыгрыша. \nДля принятия участия введите: ' +
                                         contestInstruction.get(event.peer_id) + '\n\n До окончания розыгрыша: ' + str(
                                     setupTimer.get(event.peer_id)) +
                                    'мин.\n\nУчастники в розыгрыше: ' +
                                         ', '.join(asyncio.run(contestMember(event.peer_id))))
            except vk_api.exceptions.ApiError:
                asyncio.run(contestCleaner(event.user_id))