# QUESTIONS:
- нужен ли active_player? ->  а какая альтернатива? каждый раз использовать `players_to_move[0]`?

# FIXES:
- [ ] fix: Когда игра закончена и отображены результаты, если хост нажмет "закрыть" результаты и "начать игру", а остальные игроки не нажали "закрыть" результаты, то хост попадает в игру, а игроки остаются в лобби
- [ ] fix: для всех карт в деке несмотря на tier карты, ограничить max_team количеством игроков в игре
- [ ] fix: если играют 3 игроков и они строят подряд с 1 по 5 tiers одной и той же семьи зданий, то после 5го раунда будет ошибка, так как в деке осталось всего 2 семьи, а показать можно только первые tiers из этих двух семей, т.е. всего 2 карты. А надо 3 карты показать (sample to draw is larger than available cards)
- [ ] fix: когда тянем карты из колоды для след. раунда, из успешно построенных выбирать только самые высокие tiers для каждой отдельной семьи
- [ ] fix: не давать нажать подтвердить выбор команды пока не выбрано нужное кол-во игроков

# FEATURES:
- [ ] I feat: reconnect (обработка события выхода из лобби)
- [ ] II feat: выбор названия города в лобби
- [ ] feat: чины (vacancy)
        - on_failure: 
            - перераспределить/забрать чины игроков из команды

- [x] feat: штрафы: только лидер на четных, минимальный вкладчик на нечетных
        

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
