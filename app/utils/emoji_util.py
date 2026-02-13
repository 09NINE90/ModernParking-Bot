import random

car_emojis = [
    "<tg-emoji emoji-id=\"5339222125108548762\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341362414686328905\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341762027033482961\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339520182953989991\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339244944269791114\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339163683488553489\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339078028955767266\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339150313255361475\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341452162322947110\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339447147035120095\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339428416682749581\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339151344047512399\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341360052454315229\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341644993469632309\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341522505297319672\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339472530291840318\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341416282166155673\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341465163188950382\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341506046982640706\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339073463405532065\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341628174377702653\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339254534931762823\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341790498371686706\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341365949444411128\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5339056768867652412\">🚗</tg-emoji>",
    "<tg-emoji emoji-id=\"5341509753539418394\">🚗</tg-emoji>"
]

statistics_emoji = "<tg-emoji emoji-id=\"5231200819986047254\">📊</tg-emoji>"
warn_emoji = "<tg-emoji emoji-id=\"5447644880824181073\">⚠️</tg-emoji>"
info_emoji = "<tg-emoji emoji-id=\"5334544901428229844\">ℹ️</tg-emoji>"
create_emoji = "<tg-emoji emoji-id=\"5413879192267805083\">📝</tg-emoji>"
trash_emoji = "<tg-emoji emoji-id=\"5445267414562389170\">🗑️</tg-emoji>"
sber_emoji = "<tg-emoji emoji-id=\"5258383045232183945\">✅</tg-emoji>"
reminder_emoji = "<tg-emoji emoji-id=\"5458603043203327669\">🔔</tg-emoji>"
congratulation_emoji = "<tg-emoji emoji-id=\"5461151367559141950\">🎉</tg-emoji>"
back_emoji = "<tg-emoji emoji-id=\"5258236805890710909\">🔙</tg-emoji>"
clock_emoji = "<tg-emoji emoji-id=\"5413704112220949842\">⏰</tg-emoji>"
spot_emoji = "<tg-emoji emoji-id=\"5391032818111363540\">📍</tg-emoji>"
date_emoji = "<tg-emoji emoji-id=\"5413879192267805083\">📅</tg-emoji>"
eyes_emoji = "<tg-emoji emoji-id=\"5210956306952758910\">👀</tg-emoji>"
save_emoji = "<tg-emoji emoji-id=\"5462956611033117422\">💾</tg-emoji>"
waiting_emoji = "<tg-emoji emoji-id=\"5440621591387980068\">⌛️</tg-emoji>"
canceled_emoji = "<tg-emoji emoji-id=\"5210952531676504517\">❌</tg-emoji>"
not_found_emoji = "<tg-emoji emoji-id=\"5458378137240877666\">🤷</tg-emoji>"

sber_spot_emoji = "<tg-emoji emoji-id=\"5427335835907293424\">📍</tg-emoji>"
sber_back_emoji = "<tg-emoji emoji-id=\"5420128322438851607\">🔙</tg-emoji>"
sber_black_logo_emoji = "<tg-emoji emoji-id=\"5472242841428199049\">✅</tg-emoji>"
sber_dot_emoji = "<tg-emoji emoji-id=\"5433783127279435047\">▫️</tg-emoji>"
sber_arrow_emoji = "<tg-emoji emoji-id=\"5427343150236607668\">➡️</tg-emoji>"
sber_accept_emoji = "<tg-emoji emoji-id=\"5426986105310313313\">✅️</tg-emoji>"
sber_date_emoji = "<tg-emoji emoji-id=\"5427170638580185994\">📅</tg-emoji>"

def get_random_car_emoji():
    return random.choice(car_emojis)
