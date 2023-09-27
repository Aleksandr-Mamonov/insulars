# QUESTIONS:
- Зачем sid в room_players?
- нужен ли active_player? ->  а какая альтернатива? каждый раз использовать `players_to_move[0]`?
# FIXES:
- [ ]fix: когда в конце игры у нескольких игроков одинаковое кол-во очков, надо писать, что они все победители (сейчас пишет, что только один выиграл)
- [x]fix: winner должен определяться после того, как применится эффект последнего раунда, а не до этого

# FEATURES:
- [ ] I feat: окно с результатом раунда висит до того, пока не закроют
- [ ] I feat: отображать кто в команде после выбора карты и команды, чтоб игроки знали
- [ ] I feat: опция: Лидер видит только награду, другие игроки видят только наказание.
- [ ] I feat: опция: сделать видимость очков всех игроков (в виде таблицы)
- [ ] I feat: добавить локализацию карточек на русском, переписать и сделать понятными эффекты на карточках
- [x] I feat: если игроки начинают следующую игру тем же составом, то первым ходит уже другой игрок (ротация)
- [x] I feat: показывать в конце игры рейтинг игроков с очками и победителя, передать рейтинг игроков в конце игры
- [ ] II feat: построенное здание должно давать очки лидеру
- [ ] II feat: порядок хода членов команды должен быть не последовательный, а асинхронный
- [ ] II feat: создать несколько колод - колода на 4ых игроков, колода на 5ых ...
- [ ] III feat: cделать возврат в сессию (если игрок случайно закрыл вкладку, а потом снова открыл её)
- [ ] ? feat: возможность дать деньги другому игроку
- [ ] ? feat: после выбора карточки лидер сам решает сколько участников взять в команду

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
    - добавить карточки, с эффектами на всех игроков в игре, а не только команде
    - Условие на некоторых карточках: Кто вкинул больше всех избегает наказания (или получает меньшее наказание)
    - обнулить действующие штрафы
    - карточка на 2ух, которая меняет количество очков у игроков при провале, а при успехе - х50% очки для каждого
    - Переплата идет тому, кто больше вложил, кто меньше вложил или лидеру
    vНедоплату платит лидер