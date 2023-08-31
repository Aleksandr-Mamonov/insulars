ROADMAP:
Сделать механизм начала игры
Визуальное оформление
    css framework

Vue.js: lifecycle, data binding


TODO:
read - conventionalcommits.org

Стол:
+ 1.1 каждый раунд есть лидер (тот, кто первый ходит в раунде)
карта = {название, сумма постройки, кол-во строителей (от m до n), результат при выполнении, результат при провале}
+ 1.2 CREATE TABLE cards (все возможные карты)
name
points_to_succeed
min_team
max_team
on_success
on_failure

+ # TODO: добавить game_id в game
+ 1.3 В конкретную игру мы собираем колоду
CREATE TABLE game_deck (колода для данной игры)
game_id
card_id PRIMARY KEY
card_name
available BOOLEAN

+ 1.4 каждый раунд выпадает K карт со зданиями
+ добавить table=[К рандомно выпавших карт (CARD_ID)] в game
+ table меняется с новым раундом

+ добавить selected_cards=[выбранная(ые) лидером карты (CARD_ID)]в game
+ selected_cards обнуляется с началом нового раунда

2.1 после обсуждения лидер выбирает карт(ы) для раунда
2.2 лидер выбирает команду для раунда (P игроков)
переход хода к след.игроку

3 после этого игроки выбранной команды по очереди скидываются в копилку, исходя из стоимости здания и договоренности
? Что делают игроки, которых не выбрали в команду в данном раунде?

4 после того, как все скинулись идет проверка построено ли здание (сумма в копилке д.б. >= суммы постройки здания)
применяется соответствующий результат (либо построено, либо нет)

1 начало следующего раунда

После последнего раунда идет подсчет результатов игры
Побеждает тот, у кого больше очков

TODO:
Deploy
Websockets Flask functioning
Interface 

Варианты on_success:
- все члены команды получают сразу же после окончания раунда N очков
- все члены команды получают в течение R раундов по N очков
- лидер решает как распределить сумму между членами команды, полученную за успешный раунд
- все члены команды будут лидерами 2 хода подряд
- члены команды кроме лидера получают очки, а лидер остается лидером на следующий раунд
- все члены команды в будущем, когда будут лидерами могут 1 раз поменять карты, выпавшие на стол (вытянуть еще раз)

Варианты on_failure:
- все члены команды лишаются очков сразу же по окончании раунда
- все члены команды лишаются в течение R раундов по N очков
- лидер решает сколько очков отнимется (из общей суммы, которую необходимо отнять) у каждого из членов команды
- только лидер лишается N очков
- только члены команды кроме лидера лишаются по N очков
- лидер пропускает свое следующее лидерство
- сумма N вычитается у случайного игрока из команды. Все остальные ничего не теряют
- у каждого члена команды вычитается случайно выбранное число из списка чисел. Например, в команде 3 человека. В условии on_failure список [10,20,30]. У каждого точно вычтется одно из этих чисел, но неизвестно у какого сколько.
- лидер в свое следующее лидерство выбирает только команду, но не карту.
