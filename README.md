# QUESTIONS:
- нужен ли active_player? ->  а какая альтернатива? каждый раз использовать `players_to_move[0]`?

# FIXES:
- [ ] fix: Когда игра закончена и отображены результаты, если хост нажмет "закрыть" результаты и "начать игру", а остальные игроки не нажали "закрыть" результаты, то хост попадает в игру, а игроки остаются в лобби

# FEATURES:
- [ ] feat: 
1) создать семейства
дека собирается: сколько игроков столько и семейств
выборка из 1го тира
если есть построенные 1го тира, то к ней добавляется эта карта 2го тира
если карта построена, то она идет в биту; если нет - то возвращается в колоду
генерация награды за карту (100% за 1 раунд, 120% за 3 раунда, 150% за 5 раундов) для каждого tier
1,3,5 tiers дают уникальную для каждого семейства пользу или вред (card['feature']):
    - стоимость здания (transport уменьшает, shopping увеличивает)
    - награда за постройку (education увеличивает, religion уменьшает)
    - зарплата чиновников (government увеличивает, culture уменьшает)
    - безусловный базовый доход (food увеличивает, medicine уменьшает)
    - случайный базовый доход (entertainment увеличивает, finance уменьшает)

- [ ] I feat: reconnect (обработка события выхода из лобби)
- [ ] II feat: выбор названия города в лобби
- [ ] feat: чины
        - чин получает тот, кто больше всего вложил
        - чин получает зарплату
        - on_failure: 
            - большой штраф случайному игроку
            - перераспределить/забрать чины игроков из команды
            
- [ ] feat: скрытые роли

        

- [ ] I feat: создать несколько колод - колода на 4ых игроков, колода на 5ых ...
- [ ] III feat: cделать возврат в сессию (если игрок случайно закрыл вкладку, а потом снова открыл её)
- [ ] ? feat: возможность дать деньги другому игроку
- [ ] ? feat: после выбора карточки лидер сам решает сколько участников взять в команду
- [ ] ? feat: порядок хода членов команды должен быть не последовательный, а асинхронный
- [ ] feat: создать новую игру тем же составом

# TESTS:
- [ ] написать тесты для функций, которые не используют бд и сокеты
- [ ] apply_effects, 
- [ ] cancel_effects, 
- [ ] populate_...,
- [ ] браузерные тесты

# IDEAS: ЦЕЛЬ - игра должна подталкивать на веселое поведение
- растянуть штрафы на много раундов
- добавить мотивацию для лидера: (д.б. бонус и штраф для лидера)
- перед выбором команды лидер должен иметь какой-то бонус
- больше карточек на команду из 3+ игроков, а не на 1-2 игрока
- на 2ух игроков - более специфичные карты
- Добавить кроме очков(ликвидных) неликвидные активы, которые влияют на подсчет рейтинга: игрок выбирает либо получить 20 очков, либо актив стоимостью 15, который он уже (почти никогда) не теряет
### Спецкарты:
- взять кредит - оплатить постройку, но должен вернуть через 2 хода
- узнать сколько очков у конкретного игрока
- отодвинуть расплату на следующий ход
- остаться лидером еще на один ход
- тебя не могут выбрать в команду в следующем ходе
- удваивается количество очков, которые ты получишь если построишь в следующем раунде, когда будешь в команде
### Эффекты карт:
- Условие на некоторых карточках: Кто вкинул больше всех избегает наказания (или получает меньшее наказание)
- карточка на 2ух, которая меняет количество очков у игроков при провале, а при успехе - х50% очки для каждого
- Переплата идет тому, кто больше вложил, кто меньше вложил или лидеру
- Временная видимость очков игроков
- построенное здание должно давать очки лидеру
