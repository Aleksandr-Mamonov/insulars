# QUESTIONS:
- нужен ли active_player? ->  а какая альтернатива? каждый раз использовать `players_to_move[0]`?

# FIXES:
- [ ] fix: Когда игра закончена и отображены результаты, если хост нажмет "закрыть" результаты и "начать игру", а остальные игроки не нажали "закрыть" результаты, то хост попадает в игру, а игроки остаются в лобби
# FEATURES:
- [ ] I feat: создать несколько колод - колода на 4ых игроков, колода на 5ых ...
- [ ] III feat: cделать возврат в сессию (если игрок случайно закрыл вкладку, а потом снова открыл её)
- [ ] ? feat: возможность дать деньги другому игроку
- [ ] ? feat: после выбора карточки лидер сам решает сколько участников взять в команду
- [ ] ? feat: порядок хода членов команды должен быть не последовательный, а асинхронный

# TESTS:
- [ ] написать тесты для функций, которые не используют бд и сокеты
- [ ] apply_effects, 
- [ ] cancel_effects, 
- [ ] populate_...,

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
