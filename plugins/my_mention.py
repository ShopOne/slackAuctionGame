# coding: utf-8

from slackbot.bot import respond_to
from slackbot.bot import default_reply
from run import client
from plugins.person import Person
from plugins.progress import Progress
import random
import time
import threading
import datetime


ITEM_DICT = ["りんご", "みかん", "にんじん", "かぼちゃ",
             "ちくわ", "カモメ", "乾電池", "コショウ",
             "扇風機", "カーテン", "えんぴつ", "桃",
             "ガム", "ぶどう", "いちご", "バイク",
             "パソコン", "針金", "輪ゴム", "靴下",
             "クッション", "うどん", "お茶", "犬",
             "ゲーム", "モンブラン", "なべ", "フライパン"]
RARE_ITEM_DICT = ["風来のシレン", "青春", "10万円",
                  "PSVita", "単位"]
RARE_RATE = 0.05
FIRST_MONEY = 300
AUCTION_START_G = 1
INTERVAL = 10
WAIT_AUCTION = 3

now_price = 0
least_count = 0
latest_bid_id = ""
participant = {}
auction_item = []
auction_progress = 0
now_progress = Progress.FREE
occor_bid = False


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def reset():
    global participant, auction_item, auction_progress
    global now_progress, now_price, least_count, latest_bid_id
    global occor_bid
    now_price = 0
    least_count = 0
    latest_bid_id = ""
    participant.clear()
    auction_item.clear()
    auction_progress = 0
    now_progress = Progress.FREE
    occor_bid = False


def end_game(message):
    winner_names = []
    winner_buy = -100
    winner_money = -100
    for i in participant.keys():
        buy = 0
        for j in participant[i].like:
            if j in participant[i].buy:
                buy += 1
        if (buy > winner_buy) or \
                (buy == winner_buy and participant[i].money > winner_money):
            winner_buy = buy
            winner_money = participant[i].money
            winner_names = [participant[i].name]
        elif(buy == winner_buy and participant[i].money == winner_money):
            winner_names.append(participant[i].name)

    message.send(str(*winner_names)+"さんが勝者です！ おめでとうございます！")
    result = ""
    for i in participant.keys():
        result += participant[i].name + "\n"
        result += "所持金:"+str(participant[i].money) +\
            "   購入品:" + str(participant[i].buy) +\
            "   買いたかった物:" + str(participant[i].like) + "\n"
    result = result.rstrip('\n')
    message.send(result)
    reset()


def decrease_least(message):
    global least_count, occor_bid
    print_time = False
    if least_count == WAIT_AUCTION:
        print_time = True

    least_count -= 1
    if occor_bid and least_count == 0:
        print_time = True
        least_count = 1
        message.send("延長が発生しました")

    occor_bid = False
    if print_time:
        end_time = datetime.datetime.now()
        end_time += datetime.timedelta(seconds=10 * least_count)
        message.send("終了予定は"
                     + str(end_time.hour) + ":"
                     + str(end_time.minute) + ":"
                     + str(end_time.second) + "です")


def auction_schedule(message):
    global least_count, occor_bid, auction_progress
    base_time = time.time()
    next_time = 0
    least_count = 1
    occor_bid = False
    while least_count > 0:
        t = threading.Thread(target=decrease_least, args=(message,))
        t.start()
        next_time = ((base_time - time.time()) % INTERVAL) or INTERVAL
        time.sleep(next_time)
    send_text = ""
    if latest_bid_id != "":
        send_text = participant[latest_bid_id].name + "さん" + \
                str(now_price) + "Gで落札！"
        participant[latest_bid_id].money -= now_price
        participant[latest_bid_id].buy.append(auction_item[auction_progress])
    else:
        message.send("誰も入札しませんでした")

    message.send(send_text)
    auction_progress += 1
    start_new_auction(message)


def start_new_auction(message):
    if auction_progress == len(auction_item):
        end_game(message)
        return
    global now_price, latest_bid_id
    latest_bid_id = ""
    now_price = AUCTION_START_G
    now_mon = "所持金\n"
    for i in participant.keys():
        now_mon += participant[i].name + ": " + str(participant[i].money)
        if i != len(participant):
            now_mon += "\n"
    message.send(now_mon)
    message.send("商品は" + auction_item[auction_progress] + "です(" +
                 str(auction_progress+1) + "/" + str(len(auction_item)) + ")")
    auction_schedule(message)


@default_reply()
def default_func(message):
    if now_progress == Progress.REQRUIT:
        user_name = message.user["profile"]["display_name"]
        user_id = message.body['user']
        participant[user_id] = Person(user_id, user_name, FIRST_MONEY)
        message.reply("参加を受け付けました")
    else:
        message.reply("ウグゥーーーーーーーーーーッ!!!")


@respond_to(r"bid \d+")
def bid_func(message):
    global now_price, latest_bid_id, occor_bid
    if now_progress != Progress.ONGAME:
        message.send("今は何も出品していません")
        return
    text = message.body['text']
    parsed_text = text.split()
    if(len(parsed_text) != 2 and not is_integer(parsed_text[1])):
        message.send("フォーマットに不具合があります")
        return
    user_id = message.body['user']
    bid_price = int(parsed_text[1])
    if now_price >= bid_price:
        message.send("現在の価格" + str(now_price) + "以下の金額です")
        return
    if participant[user_id].money < bid_price:
        message.reply("Gが足りていません")
    else:
        message.reply(str(bid_price) + "Gでの入札を確認しました")
        now_price = bid_price
        latest_bid_id = user_id
        occor_bid = True


@respond_to("help")
def help_func(message):
    message.send("""\
help ヘルプコマンド
rule ルール説明
init ゲーム準備
start ゲーム開始(init後)
bid 『金額』 入札

以下ルール
全員所持金300円でオークションを行います。
全ての人に、オークションで欲しい物が2つ決められ、DMで伝えられます。
これは他の人には分からず、被っている場合もあります。
それぞれの好きな物は、必ず1度のみオークションに出品されます。
全てのオークションが終了した時点で欲しい物を一番多く持っている人が勝者となります。
同じ数だけ持っているのなら、残ったお金が多い人が勝者となります。

オークションには、皆にとってどうでも良い品が出る場合もあります。""")


@respond_to("ok")
def ok_func(message):
    global auction_times, participant, now_progress
    if now_progress != Progress.REQRUIT:
        message.send("確かに僕もOKだと思います")
        return
    if len(participant) == 0:
        message.send("誰も参加していません")
        return
    auction_times = len(participant) + random.randint(0, len(participant)+2)
    # 辞書サイズを超えないように
    auction_times = min(auction_times, len(RARE_ITEM_DICT + ITEM_DICT))
    auction_times = max(2, auction_times)

    use_dict = random.sample(ITEM_DICT, len(ITEM_DICT))
    use_rare = random.sample(RARE_ITEM_DICT, len(RARE_ITEM_DICT))
    dict_idx = rare_idx = 0
    for i in range(auction_times):
        if dict_idx == len(use_dict) or random.random() <= RARE_RATE:
            auction_item.append(use_rare[rare_idx])
            rare_idx += 1
        else:
            auction_item.append(use_dict[dict_idx])
            dict_idx += 1

    for i in participant.keys():
        participant[i].like = random.sample(auction_item, 2)
        client.chat_postMessage(
            channel=participant[i].id,
            text=str(participant[i].like)+"を落札して下さい。")
    now_progress = Progress.ONGAME
    message.send("""メンションで『bid "金額"』 ("と『』不要)で入札します
金額は整数のみです。
一定時間経つと次のオークションへ移ります
時間はおおよそ30秒、ただし残り時間が10秒未満の間に入札された場合は時間が延長します""")
    start_new_auction(message)


@respond_to("init")
def start_func(message):
    global now_progress
    if(now_progress != Progress.FREE):
        message.send("今はinit出来ません")
        return

    message.send("""ゲーム参加者を募集します
参加する人はなんでも良いのでこのbotにリプライを送信して下さい。
全員参加したら、okとリプライして下さい。""")
    now_progress = Progress.REQRUIT


@respond_to("rule")
def rule_func(message):
    message.send("""\
全員所持金300円でオークションを行います。
全ての人に、オークションで欲しい物が2つ決められ、DMで伝えられます。
これは他の人には分からず、被っている場合もあります。
その物は、必ず1度のみオークションに出品されます。
全てのオークションが終了した時点で、欲しい物を一番多く持っている人、
同じ数だけ持っているのなら、残ったお金が多い人が勝者となります。

オークションには、皆にとってどうでも良い品が出る場合もあります。""")
