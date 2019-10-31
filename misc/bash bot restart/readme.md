#### Достаточно костыльное решение проблемы ночных отвалов


Проблема модуля vk_api проявляется при ночных рестарстах серверов VK. 

Отсутсвие обработчика для модуля requests стабильно приводит к открытому исключению во время дисконнектов от VK:

```python
Traceback (most recent call last):
  File "/home/p2love/main.py", line 148, in <module>
    for event in longpoll.listen():
  File "/home/p2love/.local/lib/python3.7/site-packages/vk_api/longpoll.py", line 621, in listen
    for event in self.check():
  File "/home/p2love/.local/lib/python3.7/site-packages/vk_api/longpoll.py", line 560, in check
    timeout=self.wait + 10
  File "/usr/lib/python3.7/site-packages/requests/sessions.py", line 525, in get
    return self.request('GET', url, **kwargs)
  File "/usr/lib/python3.7/site-packages/requests/sessions.py", line 512, in request
    resp = self.send(prep, **send_kwargs)
  File "/usr/lib/python3.7/site-packages/requests/sessions.py", line 622, in send
    r = adapter.send(request, **kwargs)
  File "/usr/lib/python3.7/site-packages/requests/adapters.py", line 526, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='im.vk.com', port=443): Read timed out. (read timeout=35)
```

О проблеме [писал в issue репозитория vk_api,](https://github.com/python273/vk_api/issues/302 "писал в issue репозитория vk_api,") на что получил только теоритическое решение проблемы в виде оборачивания слушалки лп в try/except самостоятельно.

Будем надеяться на то, что [python273](https://github.com/python273 "python273") в скором времени обновит либу и добавит обработчик.
Пока что пользуемся таким костылем придуманным [fgff](https://github.com/fgff "fgff") для linux серверов.

- Использование:

1. - Закидываем start.sh в одну папку с main.py
2. - Делаем chmod +x start.sh
3. - Запускаем `./start.sh` или `nohup ./start.sh` 
(второе для того, чтобы процесс не убивался при закрытии терминала)

- Отключение скрипта, запущенного через nohup:

1. - Выполняем в терминале `ps -ef`
2. - Ищем процесс содержащий **/start.sh** в конце
3. - Также ищем процесс с **python3 main.py**
4. - Делаем `kill <pid> <pid>`, где вместо `<pid>` мы подставляем id наших процессов из пункта 2 и 3